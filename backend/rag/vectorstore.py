"""
vector_store.py

Manages storing and retrieving document embeddings
using ChromaDB.
"""

from typing import List
import logging
import uuid
import chromadb
import numpy as np
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Handles all operations related to the ChromaDB vector database.
    """

    def __init__(
        self,
        collection_name: str = "Rag Chatbot Collection",
        persist_directory: str = "./chroma_db",
    ):
        """
        Initialize the ChromaDB vector store.

        Args:
            collection_name: Name of the ChromaDB collection.
            persist_directory: Directory where the database is stored.
        """

        self.collection_name = collection_name
        self.persist_directory = persist_directory

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
            user_id: str | None = None,
            filename: str | None = None,
            chat_id: str | None = None,
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

        ids = []
        documents = []
        metadatas = []
        vectors = []

        current_count = self.collection.count()

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

            ids.append(str(uuid.uuid4()))

            documents.append(chunk.page_content)

            metadata = dict(chunk.metadata)
            if user_id is not None:
                metadata["user_id"] = str(user_id)
            if filename is not None:
                metadata["filename"] = str(filename)
            if chat_id is not None:
                metadata["chat_id"] = str(chat_id)
            
            metadatas.append(metadata)

            vectors.append(embedding.tolist())

        self.collection.add(
            ids=ids,
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
        chat_id: str | None = None,
    ):
        """
        Retrieve the most similar chunks.

        Args:
            query_embedding: Embedding of the user query.
            top_k: Number of chunks to retrieve.

        Returns:
            ChromaDB query results.
        """
        where = self._build_where(user_id=user_id, chat_id=chat_id)

        query_args = {
            "query_embeddings": [query_embedding.tolist()],
            "n_results": top_k,
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
        user_id: str | None = None,
        chat_id: str | None = None,
        filename: str | None = None,
    ) -> dict | None:
        filters = []
        if user_id is not None:
            filters.append({"user_id": str(user_id)})
        if chat_id is not None:
            filters.append({"chat_id": str(chat_id)})
        if filename is not None:
            filters.append({"filename": str(filename)})

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

    def delete_chat_vectors(
        self,
        user_id: str | None = None,
        chat_id: str | None = None,
    ):
        """
        Delete all vectors belonging to a specific chat.
        """

        where = self._build_where(user_id=user_id, chat_id=chat_id)
        if where is None:
            raise ValueError("Provide user_id or chat_id before deleting vectors.")
        self.collection.delete(where=where)

        logger.info(f"Deleted vectors of chat {chat_id}")

    def delete_document_vectors(
        self,
        user_id: str | None = None,
        chat_id: str | None = None,
        filename: str | None = None,
    ):
        """
        Delete vectors belonging to a specific document.
        """

        where = self._build_where(
            user_id=user_id,
            chat_id=chat_id,
            filename=filename,
        )
        if where is None:
            raise ValueError("Provide at least one filter before deleting vectors.")
        self.collection.delete(where=where)

    def get_chat_documents(
        self,
        user_id: str | None = None,
        chat_id: str | None = None,
    ):
        """
        Return every chunk belonging to a chat.
        """

        where = self._build_where(user_id=user_id, chat_id=chat_id)
        if where is None:
            return self.collection.get()
        return self.collection.get(where=where)