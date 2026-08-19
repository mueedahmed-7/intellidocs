import re
import time

# pyrefly: ignore [missing-import]
import cv2
# pyrefly: ignore [missing-import]
import numpy as np

from .config import DATA_DIR
from .face_utils import (
    init_webcam,
    get_face_detector,
    get_face_recognizer,
    extract_embedding,
)


# ============================================================
# REGISTRATION SETTINGS
# ============================================================

# Minimum average brightness considered acceptable
MIN_BRIGHTNESS = 55

# Face width as a percentage of camera width
MIN_FACE_WIDTH_RATIO = 0.15
MAX_FACE_WIDTH_RATIO = 0.60

# Face should be reasonably close to the center
CENTER_TOLERANCE = 0.20

# Face must remain stable for this amount of time
STABLE_TIME = 0.8

# Number of registration angles
REGISTRATION_STEPS = [
    ("FRONT", "Look straight at the camera"),
    ("LEFT", "Turn your head to YOUR LEFT"),
    ("RIGHT", "Turn your head to YOUR RIGHT"),
]


# ============================================================
# USERNAME CLEANING
# ============================================================

def clean_username(username: str) -> str:
    """
    Removes unsafe characters from username.
    """

    return re.sub(
        r"[^a-zA-Z0-9_\-]",
        "",
        username,
    )


# ============================================================
# BRIGHTNESS CHECK
# ============================================================

def get_brightness(frame: np.ndarray) -> float:
    """
    Calculates average grayscale brightness.
    """

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY,
    )

    return float(np.mean(gray))


# ============================================================
# FACE POSITION / DISTANCE CHECK
# ============================================================

def analyze_face(
    frame: np.ndarray,
    face: np.ndarray,
):
    """
    Checks:

    - lighting
    - distance
    - horizontal position

    Returns:

        status_code
        status_message
        status_color
    """

    frame_height, frame_width = frame.shape[:2]

    x, y, face_width, face_height = map(
        int,
        face[:4],
    )

    # --------------------------------------------------------
    # LIGHTING
    # --------------------------------------------------------

    brightness = get_brightness(frame)

    if brightness < MIN_BRIGHTNESS:

        return (
            "LOW_LIGHT",
            "LOW LIGHT - MOVE TO A BRIGHTER AREA",
            (0, 165, 255),
        )

    # --------------------------------------------------------
    # FACE DISTANCE
    # --------------------------------------------------------

    face_width_ratio = (
        face_width / frame_width
    )

    if face_width_ratio < MIN_FACE_WIDTH_RATIO:

        return (
            "TOO_FAR",
            "TOO FAR - MOVE CLOSER",
            (0, 165, 255),
        )

    if face_width_ratio > MAX_FACE_WIDTH_RATIO:

        return (
            "TOO_CLOSE",
            "TOO CLOSE - MOVE BACK",
            (0, 165, 255),
        )

    # --------------------------------------------------------
    # FACE CENTER
    # --------------------------------------------------------

    face_center_x = (
        x + face_width / 2
    )

    frame_center_x = (
        frame_width / 2
    )

    horizontal_offset = (
        face_center_x - frame_center_x
    ) / frame_width

    if horizontal_offset < -CENTER_TOLERANCE:

        return (
            "MOVE_RIGHT",
            "MOVE RIGHT",
            (0, 165, 255),
        )

    if horizontal_offset > CENTER_TOLERANCE:

        return (
            "MOVE_LEFT",
            "MOVE LEFT",
            (0, 165, 255),
        )

    # --------------------------------------------------------
    # EVERYTHING GOOD
    # --------------------------------------------------------

    return (
        "GOOD",
        "GOOD - HOLD STILL",
        (0, 255, 0),
    )


# ============================================================
# DRAW FACE
# ============================================================

def draw_face(
    frame,
    face,
    color,
):
    """
    Draws YuNet bounding box and landmarks.
    """

    x, y, face_width, face_height = map(
        int,
        face[:4],
    )

    cv2.rectangle(
        frame,
        (x, y),
        (
            x + face_width,
            y + face_height,
        ),
        color,
        2,
    )

    # --------------------------------------------------------
    # LANDMARKS
    # --------------------------------------------------------

    for index in range(5):

        lx = int(
            face[4 + 2 * index]
        )

        ly = int(
            face[5 + 2 * index]
        )

        cv2.circle(
            frame,
            (lx, ly),
            3,
            (255, 0, 0),
            -1,
        )

    # --------------------------------------------------------
    # DETECTION CONFIDENCE
    # --------------------------------------------------------

    confidence = float(face[14])

    cv2.putText(
        frame,
        f"Conf: {confidence:.2f}",
        (
            x,
            max(20, y - 10),
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        1,
    )


# ============================================================
# DRAW TEXT
# ============================================================

def draw_text(
    frame,
    text,
    position,
    size=0.7,
    color=(255, 255, 255),
    thickness=2,
):
    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        size,
        color,
        thickness,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 65)
    print("        MULTI-ANGLE FACE REGISTRATION")
    print("=" * 65)

    # --------------------------------------------------------
    # USERNAME
    # --------------------------------------------------------

    raw_user = input(
        "Enter unique username/ID to register: "
    ).strip()

    username = clean_username(
        raw_user
    )

    if not username:

        print(
            "[ERROR] Invalid username."
        )

        return

    user_file = (
        DATA_DIR / f"{username}.npy"
    )

    # --------------------------------------------------------
    # EXISTING USER
    # --------------------------------------------------------

    if user_file.exists():

        confirm = input(
            f"[WARNING] User '{username}' already exists. "
            "Overwrite? (y/n): "
        ).strip().lower()

        if confirm != "y":

            print(
                "Registration cancelled."
            )

            return

    # --------------------------------------------------------
    # CAMERA
    # --------------------------------------------------------

    print(
        "\n[INFO] Starting camera..."
    )

    try:

        cap = init_webcam(0)

    except Exception as e:

        print(
            f"[ERROR] {e}"
        )

        return

    # --------------------------------------------------------
    # INITIAL FRAME
    # --------------------------------------------------------

    ret, frame = cap.read()

    if not ret or frame is None:

        print(
            "[ERROR] Could not read "
            "initial camera frame."
        )

        cap.release()

        return

    height, width, _ = frame.shape

    # --------------------------------------------------------
    # MODELS
    # --------------------------------------------------------

    try:

        print(
            "[INFO] Loading face detection model..."
        )

        detector = get_face_detector(
            width,
            height,
        )

        print(
            "[INFO] Loading face recognition model..."
        )

        recognizer = get_face_recognizer()

    except Exception as e:

        print(
            f"[ERROR] Failed to load models: {e}"
        )

        cap.release()

        return

    # --------------------------------------------------------
    # REGISTRATION INFORMATION
    # --------------------------------------------------------

    print("\n" + "*" * 65)

    print(
        "             FACE REGISTRATION GUIDE"
    )

    print("*" * 65)

    print(
        "You will register your face from 3 angles:"
    )

    print(
        "1. FRONT"
    )

    print(
        "2. YOUR LEFT"
    )

    print(
        "3. YOUR RIGHT"
    )

    print()

    print(
        "The camera guidance uses YOUR perspective."
    )

    print(
        "If instructed to turn LEFT, turn your actual head LEFT."
    )

    print()

    print(
        "The system will automatically capture each angle."
    )

    print(
        "No SPACE key is required."
    )

    print(
        "Press Q or ESC at any time to cancel."
    )

    print("*" * 65)


    # --------------------------------------------------------
    # STORAGE
    # --------------------------------------------------------

    embeddings = []

    # --------------------------------------------------------
    # EACH ANGLE
    # --------------------------------------------------------

    for step_index, (angle_name, instruction) in enumerate(
        REGISTRATION_STEPS
    ):

        print("\n" + "=" * 65)

        print(
            f"STEP {step_index + 1}/"
            f"{len(REGISTRATION_STEPS)}: "
            f"{angle_name}"
        )

        print(
            f"Instruction: {instruction}"
        )

        print("=" * 65)

        stable_since = None

        captured = False

        while not captured:

            ret, frame = cap.read()

            if not ret:

                print(
                    "[ERROR] Webcam feed interrupted."
                )

                cap.release()
                cv2.destroyAllWindows()

                return

            display_frame = frame.copy()

            # ------------------------------------------------
            # DETECTION
            # ------------------------------------------------

            _, faces = detector.detect(
                frame
            )

            num_faces = (
                0
                if faces is None
                else faces.shape[0]
            )

            # ------------------------------------------------
            # HEADER
            # ------------------------------------------------

            draw_text(
                display_frame,
                f"STEP {step_index + 1}/3 - {angle_name}",
                (20, 35),
                0.75,
                (255, 255, 255),
                2,
            )

            draw_text(
                display_frame,
                instruction,
                (20, 70),
                0.65,
                (255, 255, 255),
                2,
            )

            # ------------------------------------------------
            # NO FACE
            # ------------------------------------------------

            if num_faces == 0:

                stable_since = None

                draw_text(
                    display_frame,
                    "NO FACE DETECTED",
                    (20, 115),
                    0.75,
                    (0, 165, 255),
                    2,
                )

            # ------------------------------------------------
            # MULTIPLE FACES
            # ------------------------------------------------

            elif num_faces > 1:

                stable_since = None

                draw_text(
                    display_frame,
                    "ONLY ONE FACE ALLOWED",
                    (20, 115),
                    0.75,
                    (0, 0, 255),
                    2,
                )

                for detected_face in faces:

                    draw_face(
                        display_frame,
                        detected_face,
                        (0, 0, 255),
                    )

            # ------------------------------------------------
            # ONE FACE
            # ------------------------------------------------

            else:

                face = faces[0]

                (
                    status_code,
                    status_message,
                    status_color,
                ) = analyze_face(
                    frame,
                    face,
                )

                draw_face(
                    display_frame,
                    face,
                    status_color,
                )

                draw_text(
                    display_frame,
                    status_message,
                    (20, 115),
                    0.65,
                    status_color,
                    2,
                )

                # ------------------------------------------------
                # GOOD POSITION
                # ------------------------------------------------

                if status_code == "GOOD":

                    if stable_since is None:

                        stable_since = (
                            time.time()
                        )

                    stable_duration = (
                        time.time()
                        - stable_since
                    )

                    # --------------------------------------------
                    # PROGRESS
                    # --------------------------------------------

                    progress = min(
                        stable_duration
                        / STABLE_TIME,
                        1.0,
                    )

                    progress_width = int(
                        400 * progress
                    )

                    cv2.rectangle(
                        display_frame,
                        (20, 145),
                        (
                            420,
                            165,
                        ),
                        (80, 80, 80),
                        2,
                    )

                    cv2.rectangle(
                        display_frame,
                        (20, 145),
                        (
                            20 + progress_width,
                            165,
                        ),
                        (0, 255, 0),
                        -1,
                    )

                    draw_text(
                        display_frame,
                        "HOLD STILL...",
                        (20, 195),
                        0.6,
                        (255, 255, 255),
                        2,
                    )

                    # --------------------------------------------
                    # CAPTURE
                    # --------------------------------------------

                    if (
                        stable_duration
                        >= STABLE_TIME
                    ):

                        print(
                            f"[INFO] Capturing "
                            f"{angle_name} embedding..."
                        )

                        try:

                            embedding = (
                                extract_embedding(
                                    recognizer,
                                    frame,
                                    face,
                                )
                            )

                            embeddings.append(
                                embedding
                            )

                            print(
                                f"[SUCCESS] "
                                f"{angle_name} captured."
                            )

                            print(
                                f"[INFO] Embedding shape: "
                                f"{embedding.shape}"
                            )

                            captured = True

                            # --------------------------------
                            # CAPTURE MESSAGE
                            # --------------------------------

                            draw_text(
                                display_frame,
                                f"{angle_name} CAPTURED!",
                                (20, 235),
                                0.8,
                                (0, 255, 0),
                                2,
                            )

                            cv2.imshow(
                                "Face Registration",
                                display_frame,
                            )

                            cv2.waitKey(
                                800
                            )

                        except Exception as e:

                            print(
                                "[ERROR] Failed to "
                                f"extract embedding: {e}"
                            )

                            cap.release()
                            cv2.destroyAllWindows()

                            return

                else:

                    # Reset stability timer whenever
                    # the face position is not good.
                    stable_since = None

            # ------------------------------------------------
            # FOOTER
            # ------------------------------------------------

            draw_text(
                display_frame,
                "Q / ESC: Cancel",
                (
                    20,
                    height - 20,
                ),
                0.55,
                (255, 255, 255),
                1,
            )

            # ------------------------------------------------
            # SHOW WINDOW
            # ------------------------------------------------

            cv2.imshow(
                "Face Registration",
                display_frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key in [
                ord("q"),
                ord("Q"),
                27,
            ]:

                print(
                    "\n[INFO] Registration cancelled."
                )

                cap.release()
                cv2.destroyAllWindows()

                return

        # ----------------------------------------------------
        # PREPARE FOR NEXT ANGLE
        # ----------------------------------------------------

        if step_index < len(
            REGISTRATION_STEPS
        ) - 1:

            next_angle = REGISTRATION_STEPS[
                step_index + 1
            ][0]

            print(
                f"\n[INFO] Next angle: {next_angle}"
            )

            # Short pause between angles
            time.sleep(0.5)

    # ========================================================
    # SAVE ALL EMBEDDINGS
    # ========================================================

    try:

        # Expected shape:
        #
        # (3, 128)
        #
        # FRONT
        # LEFT
        # RIGHT

        embeddings_array = np.array(
            embeddings,
            dtype=np.float32,
        )

        if embeddings_array.shape != (
            3,
            128,
        ):

            print(
                "[ERROR] Unexpected embedding "
                f"shape: {embeddings_array.shape}"
            )

            cap.release()
            cv2.destroyAllWindows()

            return

        np.save(
            user_file,
            embeddings_array,
        )

        print("\n" + "=" * 65)

        print(
            "       REGISTRATION COMPLETE"
        )

        print("=" * 65)

        print(
            f"User: {username}"
        )

        print(
            f"Saved to: {user_file}"
        )

        print(
            f"Embedding shape: "
            f"{embeddings_array.shape}"
        )

        print()

        print(
            "Registered angles:"
        )

        print(
            "  1. FRONT"
        )

        print(
            "  2. LEFT"
        )

        print(
            "  3. RIGHT"
        )

        print()

        print(
            "No raw face photographs were saved."
        )

        print("=" * 65)

    except Exception as e:

        print(
            f"[ERROR] Failed to save "
            f"face representations: {e}"
        )

    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    cap.release()

    cv2.destroyAllWindows()

    print(
        "\nWebcam closed."
    )


if __name__ == "__main__":
    main()