"""Stable paths and validated runtime settings used by the backend."""

import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"

# The root .env is intentionally loaded before any setting is derived from it.
# This keeps local data under the project while still allowing deployments to
# provide their own persistent mount via PERSISTENT_DATA_DIR.
load_dotenv(ENV_FILE)

# Local development continues to use backend/; deployments can point this at a
# mounted disk so uploads and vectors survive service restarts.
_data_directory = Path(os.getenv("PERSISTENT_DATA_DIR", "data")).expanduser()
DATA_DIR = _data_directory if _data_directory.is_absolute() else (PROJECT_ROOT / _data_directory).resolve()
UPLOAD_DIR = DATA_DIR / "uploads"
CHROMA_DIR = DATA_DIR / "chroma_db"


def _required_setting(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required configuration: {name}.")
    return value


JWT_SECRET_KEY = _required_setting("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256").strip() or "HS256"
if JWT_ALGORITHM not in {"HS256", "HS384", "HS512"}:
    raise RuntimeError("JWT_ALGORITHM must be one of HS256, HS384, or HS512.")

try:
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
except ValueError as error:
    raise RuntimeError("JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be a positive integer.") from error

if JWT_ACCESS_TOKEN_EXPIRE_MINUTES < 1:
    raise RuntimeError("JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be a positive integer.")

try:
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
except ValueError as error:
    raise RuntimeError("MAX_UPLOAD_SIZE_MB must be a positive integer.") from error

if MAX_UPLOAD_SIZE_MB < 1:
    raise RuntimeError("MAX_UPLOAD_SIZE_MB must be a positive integer.")

MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip() or None
try:
    OCR_MAX_PAGES = int(os.getenv("OCR_MAX_PAGES", "100"))
except ValueError as error:
    raise RuntimeError("OCR_MAX_PAGES must be a positive integer.") from error
if OCR_MAX_PAGES < 1:
    raise RuntimeError("OCR_MAX_PAGES must be a positive integer.")
OCR_MIN_ALNUM_CHARS = 20
OCR_RENDER_SCALE = 3  # 216 DPI from PyMuPDF's 72-DPI coordinate system.

try:
    RAG_DISTANCE_THRESHOLD = float(os.getenv("RAG_DISTANCE_THRESHOLD", "1.6"))
except ValueError as error:
    raise RuntimeError("RAG_DISTANCE_THRESHOLD must be a positive number.") from error
if RAG_DISTANCE_THRESHOLD <= 0:
    raise RuntimeError("RAG_DISTANCE_THRESHOLD must be a positive number.")


def allowed_origins() -> list[str]:
    raw_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def groq_api_key() -> str:
    """Return the key only when the chat feature is used."""
    return _required_setting("GROQ_API_KEY")
