"""
vector_store.py

Manages storing and retrieving document embeddings
using ChromaDB.
"""

from pathlib import Path
from typing import List
import logging
import chromadb
import numpy as np
from langchain_core.documents import Document
from backend.config import CHROMA_DIR

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Handles all operations related to the ChromaDB vector database.
    """

    def __init__(
        self,
        collection_name: str = "Rag_Chatbot_Collection",
        persist_directory: str | Path = CHROMA_DIR,
    ):
        """
        Initialize the ChromaDB vector store.

        Args:
            collection_name: Name of the ChromaDB collection.
            persist_directory: Directory where the database is stored.
        """

        self.collection_name = collection_name
        self.persist_directory = str(Path(persist_directory).resolve())

        # Create persistent client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={
                "description": "AI Powered RAG Chatbot Vector Database"
            }
        )

        logger.info("=" * 50)
        logger.info("Vector Store Initialized")
        logger.info(f"Collection Name : {self.collection_name}")
        logger.info(f"Stored Chunks   : {self.collection.count()}")
        logger.info("=" * 50)

    def add_documents(
        self,
        chunks: List[Document],
        embeddings: np.ndarray,
        ids: list[str] | None = None,
    ):
        """
        Store document chunks and their embeddings.

        Args:
            chunks: List of chunked LangChain Documents.
            embeddings: Corresponding embedding vectors.
        """

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must be equal."
            )
        if ids is not None and len(ids) != len(chunks):
            raise ValueError("Number of vector IDs must match number of chunks.")
        if not chunks:
            return

        vector_ids = []
        documents = []
        metadatas = []
        vectors = []

        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

            vector_ids.append(ids[index] if ids else f"vector-{index}")

            documents.append(chunk.page_content)

            metadata = dict(chunk.metadata)
            
            
            metadatas.append(metadata)

            vectors.append(np.asarray(embedding).tolist())

        self.collection.add(
            ids=vector_ids,
            documents=documents,
            embeddings=vectors,
            metadatas=metadatas,
        )

        logger.info(f"Successfully stored {len(chunks)} chunks.")
        logger.info(f"Total Chunks : {self.collection.count()}")

    def similarity_search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        user_id: str | None = None,
        document_ids: list[str] | None = None,
    ):
        """
        Retrieve the most similar chunks.

        Args:
            query_embedding: Embedding of the user query.
            top_k: Number of chunks to retrieve.

        Returns:
            ChromaDB query results.
        """
        if not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer.")

        where = None
        if user_id is not None:
            where = {"user_id": str(user_id)}
        if document_ids is not None:
            document_filter = {"document_id": {"$in": [str(item) for item in document_ids]}}
            where = {"$and": [where, document_filter]} if where else document_filter

        # Chroma raises an error when n_results exceeds the number of vectors
        # matching a metadata filter. Return the empty result shape expected by
        # Retriever when this user has not uploaded any documents yet.
        matching_ids = self.collection.get(where=where, include=[])["ids"]
        if not matching_ids:
            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }

        query_args = {
            "query_embeddings": [np.asarray(query_embedding).tolist()],
            "n_results": min(top_k, len(matching_ids)),
        }
        if where is not None:
            query_args["where"] = where
        results = self.collection.query(**query_args)

        return results

    def count(self) -> int:
        """
        Return the total number of stored chunks.
        """

        return self.collection.count()

    @staticmethod
    def _build_where(
        filename: str | None = None,
        user_id: str | None = None,
    ) -> dict | None:
        filters = []
        if filename is not None:
            filters.append({"filename": str(filename)})
        if user_id is not None:
            filters.append({"user_id": str(user_id)})

        if not filters:
            return None
        if len(filters) == 1:
            return filters[0]
        return {"$and": filters}

    def get_all_documents(self):
        """
        Retrieve all stored documents.

        Returns:
            Dictionary containing all documents.
        """

        return self.collection.get()

    def delete_document(self, document_id: str):
        """
        Delete a document by its ID.

        Args:
            document_id: ChromaDB document ID.
        """

        self.collection.delete(ids=[document_id])

        logger.info(f"Deleted document: {document_id}")

    def reset(self):
        """
        Delete the entire collection and recreate it.
        Useful during development/testing.
        """

        self.client.delete_collection(self.collection_name)

        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={
                "description": "AI Powered RAG Chatbot Vector Database"
            }
        )

        logger.info("Collection has been reset successfully.")

    def delete_document_vectors(self, user_id: str, document_id: str):
        """
        Delete only vectors belonging to one authenticated user's document.
        """
        where = {
            "$and": [
                {"user_id": str(user_id)},
                {"document_id": str(document_id)},
            ]
        }
        self.collection.delete(where=where)
        logger.info("Deleted vectors for document %s", document_id)

    def get_documents(
        self,
        filename: str | None = None,
        user_id: str | None = None,
    ):
        """
        Return stored chunks, optionally filtered by filename.
        """

        where = self._build_where(filename=filename, user_id=user_id)
        if where is None:
            return self.collection.get()
        return self.collection.get(where=where)
