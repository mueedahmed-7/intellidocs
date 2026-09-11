"""
embeddings.py

Responsible for generating embeddings using
Sentence Transformers.
"""

from typing import Any, List

import logging
import numpy as np
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    Handles embedding generation using Sentence Transformers.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        """
        Initialize embedding model.

        Args:
            model_name: HuggingFace embedding model.
        """

        self.model_name = model_name
        self.model = None

    def _get_model(self) -> Any:
        """Load the embedding model only when a document or chat needs it."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully.")
        return self.model

    def generate_embeddings(
        self,
        documents: List[Document],
    ) -> np.ndarray:
        """
        Generate embeddings for LangChain documents.

        Args:
            documents: List of LangChain Documents.

        Returns:
            Numpy array of embeddings.
        """

        if not documents:
            return np.array([])

        texts = [doc.page_content for doc in documents]

        logger.info(f"Generating embeddings for {len(texts)} chunks...")

        embeddings = self._get_model().encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        logger.info(f"Generated {len(embeddings)} embeddings.")

        return embeddings

    def generate_query_embedding(
        self,
        query: str,
    ) -> np.ndarray:
        """
        Generate embedding for a user query.

        Args:
            query: User question.

        Returns:
            Query embedding.
        """

        embedding = self._get_model().encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding
