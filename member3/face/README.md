# Standalone Face Recognition Module (Phase 1 Prototype)

This module implements a modular, standalone face recognition prototype for **Member 3** of the Generic RAG Chatbot project. It uses OpenCV's deep learning-based face detection and recognition interfaces (`FaceDetectorYN` and `FaceRecognizerSF`) which are lightweight, robust, compatible with **Python 3.13**, and compile-free on Windows.

---

## 1. Project Directory Structure
```text
member3/
└── face/
    ├── __init__.py          # Package entry point and imports
    ├── config.py            # Model configurations, URLs, paths, and thresholds
    ├── face_utils.py        # Helpers: camera setup, model downloads, and metrics
    ├── register_face.py     # Interactive terminal + webcam face registration
    ├── verify_face.py       # Interactive terminal + webcam face verification
    └── README.md            # Setup, execution guides, and technical explanations
```

---

## 2. Setting Up the Environment

### Step 1: Create a Python Virtual Environment
We recommend creating a local virtual environment to isolate the project packages:
```powershell
# Open terminal at the project root directory
python -m venv venv

# Activate the virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate
# On Windows Command Prompt (CMD):
.\venv\Scripts\activate.bat
```

### Step 2: Install Dependencies
Install the required dependencies using the `requirements.txt` file located in the workspace root:
```powershell
pip install -r requirements.txt
```
*(Note: OpenCV and NumPy are prebuilt binary wheels, so this step takes less than a minute and requires no C++ compiler tools.)*

---

## 3. Running the Face Recognition Prototype

### Step A: Face Registration
Registration captures a face, extracts its 128-dimensional embedding, and saves only the embedding locally as a `.npy` file. No raw photographs are stored.

```powershell
# Run the registration command from the root workspace folder:
python -m member3.face.register_face
```

**Workflow**:
1. Enter a unique username/ID (e.g., `alice`).
2. The webcam feed will open, showing a live preview.
3. Stand in front of the camera. The system will track your face.
   - If **0 faces** are detected: A yellow status message "No face detected. Waiting..." appears.
   - If **multiple faces** are detected: A red status message "Multiple faces! Show only ONE face." appears.
   - If **exactly 1 face** is detected: A green status message "Press SPACE to Register" appears, along with landmarks and a bounding box.
4. Press **SPACE** to capture and register your face. The window will close, and `member3/face/data/alice.npy` will be saved.
5. Press **Q** or **ESC** to cancel.

---

### Step B: Face Verification
Verification loads a registered embedding and compares it with a newly scanned face from the webcam in real-time.

```powershell
# Run the verification command from the root workspace folder:
python -m member3.face.verify_face
```

**Workflow**:
1. The terminal lists all currently registered users.
2. Enter the username you wish to verify against (e.g., `alice`).
3. The webcam feed opens.
4. Once exactly **1 face** is detected, press **SPACE** to verify.
5. The window will freeze, and a banner will display:
   - **`VERIFIED: MATCH` (Green)**: The person in front of the camera matches the registered user.
   - **`FAILED: NO MATCH` (Red)**: The person does not match.
6. The terminal prints Cosine Similarity and L2 Distance details. Press any key to close the window.

---

## 4. How to Test MATCH & NO MATCH

### Testing a MATCH
1. Run `python -m member3.face.register_face` and register yourself under the name `alice`.
2. Run `python -m member3.face.verify_face` and choose to verify against `alice`.
3. Look directly at the webcam and press **SPACE**.
4. **Expected Result**: A green banner reading **`VERIFIED: MATCH`** will appear. The terminal output will show a high Cosine similarity (typically $\ge 0.50$) and a low L2 distance (typically $\le 0.90$).

### Testing a NO MATCH
1. Register another person (or make a distinct face change, or print a photograph of someone else) or simply have a friend stand in front of the camera.
2. Run `python -m member3.face.verify_face` and select `alice`.
3. Have the different person look at the camera and press **SPACE**.
4. **Expected Result**: A red banner reading **`FAILED: NO MATCH`** will appear. The terminal will show a low Cosine similarity (typically $< 0.30$) and a high L2 distance (typically $> 1.20$).

---

## 5. Technical Explanations for University Viva

If asked to explain your project in a university viva, utilize the following key concepts:

### 1. Library and Model Choice
* **Why OpenCV YuNet?** Standard Haar Cascades (using Viola-Jones framework) are fast but struggle with non-frontal faces, lighting, and occlusions. YuNet is a modern, lightweight Convolutional Neural Network (CNN) designed for edge devices. It runs fast on a standard CPU and returns coordinates for the face bounding box and 5 facial landmarks (eyes, nose, mouth corners).
* **Why OpenCV SFace?** SFace is a deep-neural-network-based face recognition model. It takes an aligned face (cropped and rotated using the 5 landmarks detected by YuNet) and maps it into a **128-dimensional embedding space** (a feature vector).
* **Why not `face_recognition` (dlib)?** `dlib` is written in C++ and has a heavy dependency on CMake and Visual Studio C++ build tools on Windows. It is difficult to compile, especially on newer Python versions like 3.13. OpenCV DNN provides the same or better accuracy, faster execution, and is distributed as a pre-compiled wheel.

### 2. The Verification Mathematics (Distance and Similarity Metrics)
To verify whether two face representations $A$ and $B$ belong to the same person, we compute two mathematical metrics:

#### Cosine Similarity
$$\text{Cosine Similarity} = \frac{A \cdot B}{\|A\|_2 \|B\|_2}$$
* **Concept**: Measures the cosine of the angle between the two 128-dimensional vectors. It evaluates directional alignment rather than magnitude.
* **Range**: $[-1.0, 1.0]$. A value of $1.0$ means the vectors point in the exact same direction (perfect match).
* **Threshold**: OpenCV SFace recommends a match when $\text{Cosine Similarity} \ge 0.363$.

#### Euclidean (L2) Distance
$$\text{Euclidean Distance} = \|A - B\|_2 = \sqrt{\sum_{i=1}^{128} (A_i - B_i)^2}$$
* **Concept**: Measures the straight-line distance between the two vector coordinates in the 128-dimensional space.
* **Range**: $[0, \infty)$. A distance of $0.0$ represents identical vectors.
* **Threshold**: OpenCV SFace recommends a match when $\text{L2 Distance} \le 1.128$.

### 3. Step-by-Step Face Processing Pipeline
1. **Frame Capture**: Read an image frame from the webcam feed using `cv2.VideoCapture`.
2. **Face Detection**: Pass the frame to `cv2.FaceDetectorYN`. It localizes the face bounding box and identifies coordinates for the 5 landmarks.
3. **Alignment & Cropping**: Use `cv2.FaceRecognizerSF.alignCrop` to rotate and resize the face so that the eyes and nose align with a standard template. This removes head tilt variations and standardizes input for the next step.
4. **Feature Extraction**: Pass the aligned face image through `cv2.FaceRecognizerSF.feature` to compute the 128-dimensional embedding (a vector representation of the face).
5. **Comparison**: Calculate Euclidean distance and Cosine similarity against the saved database embedding, checking them against thresholds to output `MATCH` or `NO MATCH`.
