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
    PyMuPDFLoader,
    TextLoader,
    Docx2txtLoader,
)

logger = logging.getLogger(__name__)


class DocumentLoader:
    

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
    }

    def __init__(self):
        pass

    def load_document(self, file_path: str) -> List[Document]:
        

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")

        suffix = path.suffix.lower()
        if suffix == ".pdf":
            loader = PyMuPDFLoader(str(path))

        elif suffix == ".docx":
            loader = Docx2txtLoader(str(path))

        elif suffix in [".txt", ".md"]:
            loader = TextLoader(str(path), encoding="utf-8")

        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        documents = loader.load()
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