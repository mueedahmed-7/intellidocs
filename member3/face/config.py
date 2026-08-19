import os
from pathlib import Path

# Base Paths
FACE_DIR = Path(__file__).resolve().parent
MODELS_DIR = FACE_DIR / "models"
DATA_DIR = FACE_DIR / "data"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Model Settings
YUNET_MODEL_NAME = "face_detection_yunet_2023mar.onnx"
SFACE_MODEL_NAME = "face_recognition_sface_2021dec.onnx"

YUNET_URL = f"https://huggingface.co/opencv/face_detection_yunet/resolve/main/{YUNET_MODEL_NAME}"
SFACE_URL = f"https://huggingface.co/opencv/face_recognition_sface/resolve/main/{SFACE_MODEL_NAME}"

YUNET_PATH = MODELS_DIR / YUNET_MODEL_NAME
SFACE_PATH = MODELS_DIR / SFACE_MODEL_NAME

# Detection Parameters
# Confidence threshold for face detection
DETECTION_THRESHOLD = 0.9  
# Non-maximum suppression threshold
NMS_THRESHOLD = 0.3        

# Recognition Match Thresholds (OpenCV Zoo standards)
# Cosine similarity threshold: MATCH if score >= MATCH_COSINE_THRESHOLD
MATCH_COSINE_THRESHOLD = 0.363  
# L2 (Euclidean) distance threshold: MATCH if score <= MATCH_L2_THRESHOLD
MATCH_L2_THRESHOLD = 1.128      

# Default camera index
DEFAULT_CAMERA_INDEX = 0
