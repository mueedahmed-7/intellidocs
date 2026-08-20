# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Form
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from member3.voice.tts.text_to_speech import speak_text

import subprocess
import sys
from pathlib import Path

# pyrefly: ignore [missing-import]
import cv2
# pyrefly: ignore [missing-import]
import numpy as np

from member3.face.face_utils import (
    get_face_detector,
    get_face_recognizer,
    extract_embedding,
    compute_cosine_similarity,
)

from member3.face.config import (
    DATA_DIR,
    MATCH_COSINE_THRESHOLD,
)


app = FastAPI(
    title="AI RAG Chatbot API",
    description="Backend API for an AI-powered RAG chatbot.",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AI RAG Chatbot Backend Running"
    }


# ============================================================
# FACE REGISTRATION
# ============================================================

@app.post("/face/register")
def register_face(
    username: str = Form(...)
):

    username = username.strip()

    safe_username = "".join(
        character
        for character in username
        if character.isalnum()
        or character in "_-"
    )

    if not safe_username:
        return {
            "success": False,
            "message": "Invalid username."
        }

    project_root = Path(__file__).resolve().parent.parent

    face_data_dir = (
        project_root
        / "member3"
        / "face"
        / "data"
    )

    user_file = (
        face_data_dir
        / f"{safe_username}.npy"
    )

    face_data_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    try:

        if user_file.exists():
            user_file.unlink()

        print()
        print("=" * 70)
        print("STARTING MEMBER 3 FACE REGISTRATION")
        print(f"Username: {safe_username}")
        print("=" * 70)

        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "member3.face.register_face",
            ],
            input=safe_username + "\n",
            text=True,
            cwd=str(project_root),
        )

        print(
            f"Registration finished: "
            f"{process.returncode}"
        )

    except Exception as e:

        print(
            f"[FACE REGISTER ERROR] {e}"
        )

        return {
            "success": False,
            "message": str(e),
        }

    if process.returncode != 0:

        return {
            "success": False,
            "message": "Face registration failed or cancelled."
        }

    if not user_file.exists():

        return {
            "success": False,
            "message": "Face data was not created."
        }

    return {
        "success": True,
        "message": "Face registration completed successfully.",
        "username": safe_username,
    }


# ============================================================
# FACE LOGIN
# ============================================================

@app.post("/face/login")
def face_login():

    print()
    print("=" * 70)
    print("STARTING PYTHON FACE LOGIN")
    print("=" * 70)

    try:

        # ----------------------------------------------------
        # Check registered users
        # ----------------------------------------------------

        DATA_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        user_files = list(
            DATA_DIR.glob("*.npy")
        )

        if not user_files:

            return {
                "success": False,
                "message": "No registered faces found."
            }

        # ----------------------------------------------------
        # Load camera
        # ----------------------------------------------------

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():

            return {
                "success": False,
                "message": "Could not open Python camera."
            }

        # ----------------------------------------------------
        # Initial frame
        # ----------------------------------------------------

        ret, frame = cap.read()

        if not ret:

            cap.release()

            return {
                "success": False,
                "message": "Could not read camera."
            }

        height, width = frame.shape[:2]

        # ----------------------------------------------------
        # Load models
        # ----------------------------------------------------

        detector = get_face_detector(
            width,
            height,
        )

        recognizer = get_face_recognizer()

        # ----------------------------------------------------
        # Load registered embeddings
        # ----------------------------------------------------

        registered_users = {}

        for file in user_files:

            try:

                username = file.stem

                embeddings = np.load(
                    file
                )

                embeddings = np.asarray(
                    embeddings,
                    dtype=np.float32,
                )

                # Make sure shape is 2D
                if embeddings.ndim == 1:
                    embeddings = embeddings.reshape(
                        1,
                        -1
                    )

                registered_users[
                    username
                ] = embeddings

            except Exception as e:

                print(
                    f"Could not load {file}: {e}"
                )

        if not registered_users:

            cap.release()

            return {
                "success": False,
                "message": "No valid face registrations found."
            }

        # ====================================================
        # CAMERA LOOP
        # ====================================================

        matched_user = None
        best_similarity = -1.0

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            display_frame = frame.copy()

            # ------------------------------------------------
            # Detect face
            # ------------------------------------------------

            _, faces = detector.detect(
                frame
            )

            if faces is None or len(faces) == 0:

                cv2.putText(
                    display_frame,
                    "NO FACE DETECTED",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 165, 255),
                    2,
                )

            elif len(faces) > 1:

                cv2.putText(
                    display_frame,
                    "ONLY ONE FACE ALLOWED",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )

            else:

                face = faces[0]

                try:

                    embedding = extract_embedding(
                        recognizer,
                        frame,
                        face,
                    )

                    # ----------------------------------------
                    # Compare against every registered user
                    # ----------------------------------------

                    best_similarity = -1.0
                    matched_user = None

                    for username, stored_embeddings in registered_users.items():

                        for stored_embedding in stored_embeddings:

                            similarity = compute_cosine_similarity(
                                embedding,
                                stored_embedding,
                            )

                            if similarity > best_similarity:

                                best_similarity = similarity
                                matched_user = username

                    # ----------------------------------------
                    # Draw face box
                    # ----------------------------------------

                    x, y, w, h = map(
                        int,
                        face[:4],
                    )

                    cv2.rectangle(
                        display_frame,
                        (x, y),
                        (x + w, y + h),
                        (0, 255, 0),
                        2,
                    )

                    cv2.putText(
                        display_frame,
                        f"Similarity: {best_similarity:.3f}",
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2,
                    )

                    # ----------------------------------------
                    # MATCH
                    # ----------------------------------------

                    if (
                        best_similarity
                        >= MATCH_COSINE_THRESHOLD
                    ):

                        cv2.putText(
                            display_frame,
                            "FACE VERIFIED",
                            (30, 90),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2,
                        )

                        cv2.putText(
                            display_frame,
                            f"User: {matched_user}",
                            (30, 125),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2,
                        )

                        cv2.imshow(
                            "Face Login",
                            display_frame,
                        )

                        # Keep verification result visible
                        # for 1.5 seconds
                        cv2.waitKey(1500)

                        break

                    else:

                        cv2.putText(
                            display_frame,
                            "FACE NOT RECOGNIZED",
                            (30, 90),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2,
                        )

                except Exception as e:

                    print(
                        f"Embedding error: {e}"
                    )

            # ------------------------------------------------
            # Instructions
            # ------------------------------------------------

            cv2.putText(
                display_frame,
                "Look at camera - Q/ESC to cancel",
                (30, height - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

            cv2.imshow(
                "Face Login",
                display_frame,
            )

            key = cv2.waitKey(1) & 0xFF

            # Cancel
            if key in [
                ord("q"),
                ord("Q"),
                27,
            ]:

                matched_user = None
                break

            # Successful match
            if (
                matched_user is not None
                and best_similarity
                >= MATCH_COSINE_THRESHOLD
            ):

                break

        # ====================================================
        # CLEANUP
        # ====================================================

        cap.release()
        cv2.destroyAllWindows()

        # ====================================================
        # RESULT
        # ====================================================

        if matched_user is not None:

            print(
                f"[SUCCESS] Face recognized: "
                f"{matched_user}"
            )

            print(
                f"[INFO] Similarity: "
                f"{best_similarity:.4f}"
            )

            return {
                "success": True,
                "username": matched_user,
                "similarity": float(
                    best_similarity
                ),
                "message": "Face login successful.",
            }

        return {
            "success": False,
            "message": "Face was not recognized.",
        }

    except Exception as e:

        print(
            f"[FACE LOGIN ERROR] {e}"
        )

        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

        return {
            "success": False,
            "message": str(e),
        }


# ============================================================
# VOICE
# ============================================================

@app.post("/voice/speak")
async def voice_speak(text: str = Form(...)):
    try:
        if not text.strip():
            return {
                "success": False,
                "message": "No text provided."
            }

        speak_text(text)

        return {
            "success": True,
            "message": "Speech completed."
        }

    except Exception as e:
        print(f"[TTS ERROR] {e}")

        return {
            "success": False,
            "message": str(e)
        }