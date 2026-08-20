import re

# pyrefly: ignore [missing-import]
import cv2
# pyrefly: ignore [missing-import]
import numpy as np

from .config import DATA_DIR
from .face_utils import (
    get_face_detector,
    get_face_recognizer,
    extract_embedding,
    verify_face_embedding,
)


def clean_identity(identity: str) -> str:
    """
    Creates a safe filename from the user's email/account ID.
    """
    return re.sub(
        r"[^a-zA-Z0-9_.@-]",
        "",
        identity.strip(),
    )


def image_to_embedding(image_bytes: bytes):
    """
    Converts a browser camera image into a face embedding.

    Returns:
        embedding, error_message
    """

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8,
    )

    frame = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR,
    )

    if frame is None:
        return None, "Could not read camera image."

    height, width = frame.shape[:2]

    try:
        detector = get_face_detector(
            width,
            height,
        )

        recognizer = get_face_recognizer()

    except Exception as e:
        return None, f"Could not load face models: {e}"

    _, faces = detector.detect(frame)

    if faces is None or len(faces) == 0:
        return None, "No face detected."

    if len(faces) > 1:
        return None, "Only one face should be visible."

    face = faces[0]

    try:
        embedding = extract_embedding(
            recognizer,
            frame,
            face,
        )

        return embedding, None

    except Exception as e:
        return None, f"Could not extract face embedding: {e}"


# ============================================================
# REGISTER FACE
# ============================================================

def register_face_images(
    identity: str,
    front_image: bytes,
    left_image: bytes,
    right_image: bytes,
):
    """
    Creates three face embeddings:

        FRONT
        LEFT
        RIGHT

    and saves them as:

        (3, 128)
    """

    safe_identity = clean_identity(identity)

    if not safe_identity:
        return {
            "success": False,
            "message": "Invalid account identity."
        }

    images = [
        ("FRONT", front_image),
        ("LEFT", left_image),
        ("RIGHT", right_image),
    ]

    embeddings = []

    for angle, image_bytes in images:

        embedding, error = image_to_embedding(
            image_bytes
        )

        if error:
            return {
                "success": False,
                "message": f"{angle}: {error}"
            }

        embeddings.append(
            embedding
        )

    embeddings_array = np.asarray(
        embeddings,
        dtype=np.float32,
    )

    if embeddings_array.shape != (3, 128):

        return {
            "success": False,
            "message": (
                "Invalid embedding shape: "
                f"{embeddings_array.shape}"
            )
        }

    user_file = (
        DATA_DIR / f"{safe_identity}.npy"
    )

    try:

        np.save(
            user_file,
            embeddings_array,
        )

    except Exception as e:

        return {
            "success": False,
            "message": f"Could not save face data: {e}"
        }

    return {
        "success": True,
        "message": "Face registration completed successfully.",
    }


# ============================================================
# FACE LOGIN
# ============================================================

def find_matching_user(
    image_bytes: bytes,
):
    """
    Searches the live face against ALL registered faces.
    """

    current_embedding, error = image_to_embedding(
        image_bytes
    )

    if error:

        return {
            "success": False,
            "match": False,
            "message": error,
        }

    registered_files = list(
        DATA_DIR.glob("*.npy")
    )

    if not registered_files:

        return {
            "success": False,
            "match": False,
            "message": "No registered faces found.",
        }

    best_user = None
    best_cosine = -1.0
    best_l2 = float("inf")

    for user_file in registered_files:

        try:

            saved_embeddings = np.load(
                user_file
            )

        except Exception:
            continue

        if saved_embeddings.ndim == 1:

            saved_embeddings = (
                saved_embeddings.reshape(1, -1)
            )

        if saved_embeddings.ndim != 2:
            continue

        for registered_embedding in saved_embeddings:

            try:

                is_match, cosine, l2 = (
                    verify_face_embedding(
                        current_embedding,
                        registered_embedding,
                    )
                )

            except Exception:
                continue

            if cosine > best_cosine:

                best_cosine = cosine
                best_l2 = l2
                best_user = user_file.stem

    # --------------------------------------------------------
    # NO GOOD MATCH
    # --------------------------------------------------------

    if (
        best_user is None
        or best_cosine < 0
    ):

        return {
            "success": True,
            "match": False,
            "message": "Face not recognized.",
        }

    # --------------------------------------------------------
    # THRESHOLD
    # --------------------------------------------------------

    from .config import MATCH_COSINE_THRESHOLD

    if best_cosine >= MATCH_COSINE_THRESHOLD:

        return {
            "success": True,
            "match": True,
            "user": best_user,
            "cosine_similarity": float(best_cosine),
            "l2_distance": float(best_l2),
            "message": "Face verified successfully.",
        }

    return {
        "success": True,
        "match": False,
        "cosine_similarity": float(best_cosine),
        "l2_distance": float(best_l2),
        "message": "Face not recognized.",
    }