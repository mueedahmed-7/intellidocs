"""
embeddings.py

Responsible for generating embeddings using
Sentence Transformers.
"""

from typing import List

import logging
import numpy as np
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

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

        logger.info(f"Loading embedding model: {self.model_name}")

        self.model = SentenceTransformer(self.model_name)

        self.embedding_dimension = (
            self.model.get_sentence_embedding_dimension()
        )

        logger.info("Embedding model loaded successfully.")
        logger.info(f"Embedding Dimension: {self.embedding_dimension}")

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

        embeddings = self.model.encode(
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

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding