import time

# pyrefly: ignore [missing-import]
import cv2
# pyrefly: ignore [missing-import]
import numpy as np

# pyrefly: ignore [missing-import]
from .config import (
    DATA_DIR,
    MATCH_COSINE_THRESHOLD,
    MATCH_L2_THRESHOLD,
)

# pyrefly: ignore [missing-import]
from .face_utils import (
    init_webcam,
    get_face_detector,
    get_face_recognizer,
    extract_embedding,
    verify_face_embedding,
)


# How long NOT MATCH stays on screen
NOT_MATCH_TIMEOUT = 30

# How long a face must remain detected before verification
STABLE_FACE_TIME = 1.0


def compare_against_registered_embeddings(
    current_embedding: np.ndarray,
    saved_embeddings: np.ndarray,
):
    """
    Compare the live face against all registered embeddings.

    Supports:

        (128,)    -> single-angle registration
        (3, 128)  -> multi-angle registration

    The highest cosine similarity is used as the best match.
    """

    saved_embeddings = np.asarray(saved_embeddings)

    # ------------------------------------------------------------
    # SINGLE-ANGLE REGISTRATION
    # ------------------------------------------------------------

    if saved_embeddings.ndim == 1:

        is_match, cos_sim, l2_dist = verify_face_embedding(
            current_embedding,
            saved_embeddings,
        )

        return (
            is_match,
            cos_sim,
            l2_dist,
            "SINGLE",
        )

    # ------------------------------------------------------------
    # MULTI-ANGLE REGISTRATION
    # ------------------------------------------------------------

    if saved_embeddings.ndim == 2:

        best_match = False
        best_cosine = -1.0
        best_l2 = float("inf")
        best_angle = "UNKNOWN"

        angle_names = [
            "FRONT",
            "LEFT",
            "RIGHT",
        ]

        for index, registered_embedding in enumerate(
            saved_embeddings
        ):

            is_match, cos_sim, l2_dist = (
                verify_face_embedding(
                    current_embedding,
                    registered_embedding,
                )
            )

            if cos_sim > best_cosine:

                best_cosine = cos_sim
                best_l2 = l2_dist
                best_match = is_match

                if index < len(angle_names):
                    best_angle = angle_names[index]
                else:
                    best_angle = f"ANGLE {index + 1}"

        return (
            best_match,
            best_cosine,
            best_l2,
            best_angle,
        )

    raise ValueError(
        f"Unsupported embedding shape: "
        f"{saved_embeddings.shape}"
    )


def draw_face_box(
    frame,
    face,
    color,
):
    """Draw face bounding box and landmarks."""

    x, y, face_w, face_h = map(
        int,
        face[:4],
    )

    cv2.rectangle(
        frame,
        (x, y),
        (x + face_w, y + face_h),
        color,
        2,
    )

    # YuNet landmarks
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

    confidence = float(face[14])

    cv2.putText(
        frame,
        f"Conf: {confidence:.2f}",
        (x, max(20, y - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        1,
    )


def draw_status(
    frame,
    text,
    color,
):
    """Draw simple status text."""

    cv2.putText(
        frame,
        text,
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        color,
        2,
    )


def verify_face():
    """
    Main reusable face verification function.

    Returns:
        True  -> face matched
        False -> face did not match, was cancelled,
                 or verification failed
    """

    print("=" * 60)
    print("       AUTOMATIC MULTI-ANGLE FACE VERIFICATION")
    print("=" * 60)

    # ------------------------------------------------------------
    # FIND REGISTERED USERS
    # ------------------------------------------------------------

    registered_users = [
        path.stem
        for path in DATA_DIR.glob("*.npy")
    ]

    if not registered_users:

        print(
            "[WARNING] No registered faces found."
        )

        print(
            "Run face registration first:"
        )

        print(
            "python -m member3.face.register_face"
        )

        return False

    print("Registered users:")

    for user in sorted(registered_users):
        print(f" - {user}")

    print("-" * 40)

    # ------------------------------------------------------------
    # SELECT USER
    # ------------------------------------------------------------

    target_user = input(
        "Enter username to verify against: "
    ).strip()

    if target_user not in registered_users:

        print(
            f"[ERROR] User '{target_user}' "
            "is not registered."
        )

        return False

    # ------------------------------------------------------------
    # LOAD REGISTERED EMBEDDINGS
    # ------------------------------------------------------------

    user_file = DATA_DIR / f"{target_user}.npy"

    try:

        saved_embeddings = np.load(
            user_file
        )

        print(
            f"[INFO] Loaded representation "
            f"for '{target_user}'"
        )

        print(
            f"[INFO] Shape: "
            f"{saved_embeddings.shape}"
        )

        if saved_embeddings.ndim == 1:

            print(
                "[INFO] Single-angle registration"
            )

        elif saved_embeddings.ndim == 2:

            print(
                "[INFO] Multi-angle registration: "
                f"{saved_embeddings.shape[0]} angles"
            )

        else:

            print(
                "[ERROR] Invalid embedding format."
            )

            return False

    except Exception as e:

        print(
            f"[ERROR] Failed to load "
            f"face representation: {e}"
        )

        return False

    # ------------------------------------------------------------
    # START CAMERA
    # ------------------------------------------------------------

    print(
        "\n[INFO] Starting camera..."
    )

    try:

        cap = init_webcam(0)

    except Exception as e:

        print(
            f"[ERROR] {e}"
        )

        return False

    # Get initial frame
    ret, frame = cap.read()

    if not ret or frame is None:

        print(
            "[ERROR] Failed to grab "
            "initial webcam frame."
        )

        cap.release()

        return False

    h, w, _ = frame.shape

    # ------------------------------------------------------------
    # LOAD MODELS
    # ------------------------------------------------------------

    try:

        detector = get_face_detector(
            w,
            h,
        )

        recognizer = get_face_recognizer()

    except Exception as e:

        print(
            f"[ERROR] Failed to load models: {e}"
        )

        cap.release()

        return False

    print(
        "\n[INFO] Camera ready."
    )

    print(
        "[INFO] Looking for one face..."
    )

    print(
        "[INFO] Verification will happen automatically."
    )

    print(
        "[INFO] No key press is required."
    )

    print(
        "[INFO] Press Q or ESC only if you "
        "want to cancel."
    )

    print()

    # ------------------------------------------------------------
    # VARIABLES
    # ------------------------------------------------------------

    face_detected_since = None

    verification_started = False

    result = None

    result_time = None

    # ------------------------------------------------------------
    # CAMERA LOOP
    # ------------------------------------------------------------

    while True:

        ret, frame = cap.read()

        if not ret:

            print(
                "[ERROR] Webcam feed interrupted."
            )

            result = "NOT MATCH"
            break

        display_frame = frame.copy()

        # --------------------------------------------------------
        # RESULT ALREADY EXISTS
        # --------------------------------------------------------

        if result is not None:

            if result == "MATCH":

                draw_status(
                    display_frame,
                    "MATCH",
                    (0, 255, 0),
                )

                cv2.putText(
                    display_frame,
                    "Identity Verified",
                    (20, 85),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

                cv2.imshow(
                    "Face Verification",
                    display_frame,
                )

                # MATCH screen stays for 2 seconds
                if (
                    time.time() - result_time
                    >= 2
                ):

                    break

            else:

                # ------------------------------------------------
                # NOT MATCH SCREEN
                # ------------------------------------------------

                elapsed = (
                    time.time()
                    - result_time
                )

                remaining = max(
                    0,
                    int(
                        NOT_MATCH_TIMEOUT
                        - elapsed
                    ),
                )

                draw_status(
                    display_frame,
                    "NOT MATCH",
                    (0, 0, 255),
                )

                cv2.putText(
                    display_frame,
                    "Verification Failed",
                    (20, 85),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    display_frame,
                    f"Closing in {remaining}s",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (180, 180, 180),
                    1,
                )

                cv2.imshow(
                    "Face Verification",
                    display_frame,
                )

                if elapsed >= NOT_MATCH_TIMEOUT:

                    break

            key = cv2.waitKey(1) & 0xFF

            if key in [
                ord("q"),
                ord("Q"),
                27,
            ]:

                result = "NOT MATCH"
                break

            continue

        # --------------------------------------------------------
        # FACE DETECTION
        # --------------------------------------------------------

        _, faces = detector.detect(
            frame
        )

        num_faces = (
            0
            if faces is None
            else faces.shape[0]
        )

        # --------------------------------------------------------
        # NO FACE
        # --------------------------------------------------------

        if num_faces == 0:

            face_detected_since = None

            draw_status(
                display_frame,
                "LOOK AT THE CAMERA",
                (0, 165, 255),
            )

        # --------------------------------------------------------
        # MULTIPLE FACES
        # --------------------------------------------------------

        elif num_faces > 1:

            face_detected_since = None

            draw_status(
                display_frame,
                "ONLY ONE FACE",
                (0, 0, 255),
            )

            for face in faces:

                draw_face_box(
                    display_frame,
                    face,
                    (0, 0, 255),
                )

        # --------------------------------------------------------
        # ONE FACE
        # --------------------------------------------------------

        else:

            face = faces[0]

            draw_face_box(
                display_frame,
                face,
                (0, 255, 0),
            )

            draw_status(
                display_frame,
                "FACE DETECTED",
                (0, 255, 0),
            )

            # ----------------------------------------------------
            # START STABILITY TIMER
            # ----------------------------------------------------

            if face_detected_since is None:

                face_detected_since = (
                    time.time()
                )

                print(
                    "[INFO] Face detected. "
                    "Stabilizing..."
                )

            stable_time = (
                time.time()
                - face_detected_since
            )

            # ----------------------------------------------------
            # AUTOMATIC VERIFICATION
            # ----------------------------------------------------

            if (
                stable_time
                >= STABLE_FACE_TIME
                and not verification_started
            ):

                verification_started = True

                print(
                    "[INFO] Face stable. "
                    "Starting automatic verification..."
                )

                try:

                    # --------------------------------------------
                    # EXTRACT LIVE EMBEDDING
                    # --------------------------------------------

                    current_embedding = (
                        extract_embedding(
                            recognizer,
                            frame,
                            face,
                        )
                    )

                    # --------------------------------------------
                    # COMPARE
                    # --------------------------------------------

                    (
                        is_match,
                        cos_sim,
                        l2_dist,
                        best_angle,
                    ) = (
                        compare_against_registered_embeddings(
                            current_embedding,
                            saved_embeddings,
                        )
                    )

                    # --------------------------------------------
                    # PRINT TECHNICAL RESULT
                    # --------------------------------------------

                    print(
                        "\n" + "=" * 55
                    )

                    print(
                        f"VERIFICATION REPORT: "
                        f"{target_user}"
                    )

                    print("=" * 55)

                    print(
                        f"Best registered angle: "
                        f"{best_angle}"
                    )

                    print(
                        f"Cosine similarity: "
                        f"{cos_sim:.4f}"
                    )

                    print(
                        f"Cosine threshold: "
                        f"{MATCH_COSINE_THRESHOLD}"
                    )

                    print(
                        f"L2 distance: "
                        f"{l2_dist:.4f}"
                    )

                    print(
                        f"L2 threshold: "
                        f"{MATCH_L2_THRESHOLD}"
                    )

                    # --------------------------------------------
                    # SET RESULT
                    # --------------------------------------------

                    if is_match:

                        result = "MATCH"

                        print(
                            "RESULT: MATCH"
                        )

                    else:

                        result = "NOT MATCH"

                        print(
                            "RESULT: NOT MATCH"
                        )

                    print("=" * 55)

                    result_time = time.time()

                except Exception as e:

                    print(
                        f"[ERROR] "
                        f"Verification failed: {e}"
                    )

                    result = "NOT MATCH"

                    result_time = time.time()

        # --------------------------------------------------------
        # FOOTER
        # --------------------------------------------------------

        cv2.putText(
            display_frame,
            f"Target: {target_user}",
            (10, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )

        cv2.imshow(
            "Face Verification",
            display_frame,
        )

        # --------------------------------------------------------
        # EXIT KEY
        # --------------------------------------------------------

        key = cv2.waitKey(1) & 0xFF

        if key in [
            ord("q"),
            ord("Q"),
            27,
        ]:

            print(
                "[INFO] Verification cancelled."
            )

            result = "NOT MATCH"
            break

    # ------------------------------------------------------------
    # CLEANUP
    # ------------------------------------------------------------

    cap.release()

    cv2.destroyAllWindows()

    print(
        "\n[INFO] Webcam closed."
    )

    print(
        "[INFO] Verification process finished."
    )

    # ------------------------------------------------------------
    # RETURN VALUE FOR INTEGRATION
    # ------------------------------------------------------------

    return result == "MATCH"


def main():

    verified = verify_face()

    print(
        f"\n[RESULT] Verification returned: "
        f"{verified}"
    )

    if verified:

        print(
            "[RESULT] Access granted."
        )

    else:

        print(
            "[RESULT] Access denied."
        )


if __name__ == "__main__":
    main()