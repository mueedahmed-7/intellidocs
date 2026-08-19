import sys
import urllib.request
import cv2
import numpy as np
from pathlib import Path
from .config import (
    YUNET_PATH, YUNET_URL,
    SFACE_PATH, SFACE_URL,
    DETECTION_THRESHOLD, NMS_THRESHOLD,
    MATCH_COSINE_THRESHOLD, MATCH_L2_THRESHOLD
)

def download_file(url: str, dest_path: Path):
    """Downloads a file from a URL to a local destination path with a progress display."""
    print(f"Downloading: {url} -> {dest_path.name}")
    
    # Custom download reporter
    def reporthook(block_num, block_size, total_size):
        read_so_far = block_num * block_size
        if total_size > 0:
            percent = min(100.0, read_so_far * 100 / total_size)
            sys.stdout.write(f"\rDownloading... {percent:.2f}% ({read_so_far / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB)")
        else:
            sys.stdout.write(f"\rDownloading... {read_so_far / (1024*1024):.2f} MB")
        sys.stdout.flush()
        
    try:
        urllib.request.urlretrieve(url, str(dest_path), reporthook)
        print("\nDownload complete!")
    except Exception as e:
        print(f"\nError downloading {url}: {e}")
        # Clean up failed download
        if dest_path.exists():
            dest_path.unlink()
        raise

def ensure_models_exist():
    """Ensures YuNet and SFace models are present, downloading them if not."""
    if not YUNET_PATH.exists():
        print(f"YuNet face detection model not found locally.")
        download_file(YUNET_URL, YUNET_PATH)
    if not SFACE_PATH.exists():
        print(f"SFace face recognition model not found locally.")
        download_file(SFACE_URL, SFACE_PATH)

def get_face_detector(width: int, height: int) -> cv2.FaceDetectorYN:
    """Initializes and returns the YuNet face detector with the specified input frame dimensions."""
    ensure_models_exist()
    return cv2.FaceDetectorYN.create(
        model=str(YUNET_PATH),
        config="",
        input_size=(width, height),
        score_threshold=DETECTION_THRESHOLD,
        nms_threshold=NMS_THRESHOLD
    )

def get_face_recognizer() -> cv2.FaceRecognizerSF:
    """Initializes and returns the SFace face recognizer."""
    ensure_models_exist()
    return cv2.FaceRecognizerSF.create(
        model=str(SFACE_PATH),
        config=""
    )

def extract_embedding(recognizer: cv2.FaceRecognizerSF, frame: np.ndarray, face_coords: np.ndarray) -> np.ndarray:
    """Aligns, crops, and extracts the 128-dimensional embedding from a face in a frame."""
    # SFace requires alignment and cropping of the detected face first
    aligned_face = recognizer.alignCrop(frame, face_coords)
    # Extracts the feature vector (returns shape 1x128)
    embedding = recognizer.feature(aligned_face)
    return embedding.flatten()

def compute_cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Computes Cosine similarity between two vectors."""
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return float(dot_product / (norm_v1 * norm_v2))

def compute_l2_distance(v1: np.ndarray, v2: np.ndarray) -> float:
    """Computes L2 (Euclidean) distance between two vectors."""
    return float(np.linalg.norm(v1 - v2))

def verify_face_embedding(v1: np.ndarray, v2: np.ndarray) -> tuple[bool, float, float]:
    """
    Compares two face embeddings using Cosine similarity.
    Calculates L2 distance for informational purposes.
    Returns: (is_match, cosine_similarity, l2_distance)
    """
    cos_sim = compute_cosine_similarity(v1, v2)
    l2_dist = compute_l2_distance(v1, v2)
    
    # Match is determined solely by Cosine Similarity threshold (L2 distance is informational)
    is_match = cos_sim >= MATCH_COSINE_THRESHOLD
    return is_match, cos_sim, l2_dist

def init_webcam(camera_index: int = 0) -> cv2.VideoCapture:
    """Attempts to initialize the webcam, raising an error if it fails."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(
            f"Failed to open webcam at index {camera_index}. "
            "Please check if it is connected or being used by another application."
        )
    return cap
