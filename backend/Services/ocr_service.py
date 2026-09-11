"""Lazy, local Tesseract OCR support for scanned PDF pages."""

import re

from backend.config import OCR_RENDER_SCALE, TESSERACT_CMD


class OCRUnavailableError(RuntimeError):
    """OCR is needed but Tesseract/pytesseract cannot be used."""


class OCRProcessingError(RuntimeError):
    """A page could not be rendered or recognised safely."""


def normalize_ocr_text(text: str) -> str:
    """Only whitespace/control cleanup; never alter recognised values or digits."""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text or "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class OCRService:
    def _pytesseract(self):
        try:
            import pytesseract
        except ImportError as error:
            raise OCRUnavailableError(
                "This PDF appears to be scanned and requires OCR, but the OCR engine is not available on the server."
            ) from error
        if TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
        try:
            pytesseract.get_tesseract_version()
        except Exception as error:
            raise OCRUnavailableError(
                "This PDF appears to be scanned and requires OCR, but the OCR engine is not available on the server."
            ) from error
        return pytesseract

    def ocr_page(self, page) -> str:
        pytesseract = self._pytesseract()
        try:
            import fitz
            from PIL import Image
            pixmap = page.get_pixmap(matrix=fitz.Matrix(OCR_RENDER_SCALE, OCR_RENDER_SCALE), alpha=False)
            image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            return normalize_ocr_text(pytesseract.image_to_string(image, lang="eng"))
        except OCRUnavailableError:
            raise
        except Exception as error:
            raise OCRProcessingError("Unable to read a scanned PDF page.") from error
