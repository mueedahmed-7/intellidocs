"""
document_service.py

Handles document upload, processing, embedding generation,
and vector storage.
"""

import logging
from pathlib import Path

from services import loader, splitter, embedding_manager, vector_store


logger = logging.getLogger(__name__)


class DocumentService:

    def __init__(
        self,
        upload_directory: str = "uploads",
    ):
        self.upload_directory = Path(upload_directory)

        self.upload_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        # RAG components
        self.loader = loader
        self.splitter = splitter
        self.embedding_manager = embedding_manager
        self.vector_store = vector_store

    def process_document(
        self,
        file_path: str,
        user_id: str,
    ):
        """
        Process a document through the complete
        RAG ingestion pipeline.
        """

        logger.info(
            f"Processing document: {file_path}"
        )

        # 1. Load document
        documents = self.loader.load_document(
            file_path
        )

        logger.info(
            f"Loaded {len(documents)} documents."
        )

        # 2. Split document
        chunks = self.splitter.split_documents(
            documents
        )

        logger.info(
            f"Generated {len(chunks)} chunks."
        )

        # 3. Add user ID to metadata
        for chunk in chunks:
            chunk.metadata["user_id"] = str(user_id)
            chunk.metadata["filename"] = Path(file_path).name

        # 4. Generate embeddings
        embeddings = (
            self.embedding_manager.generate_embeddings(
                chunks
            )
        )

        logger.info(
            f"Generated {len(embeddings)} embeddings."
        )

        # 5. Store vectors
        self.vector_store.add_documents(
            chunks=chunks,
            embeddings=embeddings,
        )

        logger.info(
            f"Document successfully processed: {file_path}"
        )

        return {
            "file_path": file_path,
            "chunks": len(chunks),
        }