"""
Face Recognition Module (Member 3 - Phase 1)

This module provides a standalone prototype for face registration and face verification 
using OpenCV YuNet (Face Detection) and SFace (Face Recognition) models.
"""

from .config import DATA_DIR, MODELS_DIR, MATCH_COSINE_THRESHOLD, MATCH_L2_THRESHOLD
from .face_utils import (
    get_face_detector,
    get_face_recognizer,
    extract_embedding,
    verify_face_embedding,
)

__version__ = "1.0.0"
