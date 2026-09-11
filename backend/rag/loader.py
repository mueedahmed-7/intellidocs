"""
loader.py

Responsible for loading supported document types into LangChain Document objects.

Supported formats:
- PDF
- DOCX
- TXT
- Markdown
"""

from pathlib import Path
from typing import List
import logging

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    Docx2txtLoader,
)
from backend.config import OCR_MAX_PAGES, OCR_MIN_ALNUM_CHARS
from backend.Services.ocr_service import OCRProcessingError, OCRService, OCRUnavailableError

logger = logging.getLogger(__name__)


class DocumentLoader:
    

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
    }

    def __init__(self, ocr_service=None):
        self.ocr_service = ocr_service or OCRService()
        self.last_extraction_info = {"extraction_method": "native", "ocr_pages": 0}

    @staticmethod
    def _has_useful_text(text: str) -> bool:
        return len("".join(character for character in (text or "") if character.isalnum())) >= OCR_MIN_ALNUM_CHARS

    def _load_pdf(self, path: Path) -> List[Document]:
        # Importing PyMuPDF only when a PDF is uploaded keeps startup light.
        import fitz

        try:
            pdf = fitz.open(str(path))
        except Exception as error:
            raise ValueError("Unable to read this PDF.") from error
        try:
            if len(pdf) > OCR_MAX_PAGES:
                raise ValueError("This PDF has too many pages to process safely.")
            documents, ocr_pages, native_pages = [], 0, 0
            for page_index, page in enumerate(pdf):
                native_text = page.get_text("text") or ""
                if self._has_useful_text(native_text):
                    text, method = native_text, "native"
                    native_pages += 1
                else:
                    text, method = self.ocr_service.ocr_page(page), "ocr"
                    if not self._has_useful_text(text):
                        raise OCRProcessingError("No usable text could be read from this scanned PDF.")
                    ocr_pages += 1
                documents.append(Document(page_content=text, metadata={"page": page_index + 1, "extraction_method": method}))
            if not documents:
                raise ValueError("No extractable text was found in this document.")
            method = "mixed" if native_pages and ocr_pages else ("ocr" if ocr_pages else "native")
            self.last_extraction_info = {"extraction_method": method, "ocr_pages": ocr_pages}
            return documents
        finally:
            pdf.close()

    def load_document(self, file_path: str) -> List[Document]:
        

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")

        suffix = path.suffix.lower()
        if suffix == ".pdf":
            documents = self._load_pdf(path)

        elif suffix == ".docx":
            loader = Docx2txtLoader(str(path))

        elif suffix in [".txt", ".md"]:
            loader = TextLoader(str(path), encoding="utf-8")

        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        if suffix != ".pdf":
            documents = loader.load()
            self.last_extraction_info = {"extraction_method": "native", "ocr_pages": 0}
        # Add metadata
        for doc in documents:
            doc.metadata["file_name"] = path.name
            doc.metadata["file_type"] = suffix
            doc.metadata["file_path"] = str(path.resolve())

        

        return documents

    def load_directory(self, directory: str) -> List[Document]:
        

        directory = Path(directory)

        if not directory.exists():
            raise FileNotFoundError(f"{directory} does not exist.")

        all_documents = []

        for file in directory.rglob("*"):

            if file.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            try:
                docs = self.load_document(str(file))
                all_documents.extend(docs)

                logger = logging.getLogger(__name__)
                logger.info(f"✓ Loaded {file.name}")

            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.exception(f"✗ Failed to load {file.name}: {e}")

        return all_documents
