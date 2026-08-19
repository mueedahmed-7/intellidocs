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
        collection_name: str = "Rag_Chatbot_Collection",
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
        if not chunks:
            return

        ids = []
        documents = []
        metadatas = []
        vectors = []

        for chunk, embedding in zip(chunks, embeddings):

            ids.append(str(uuid.uuid4()))

            documents.append(chunk.page_content)

            metadata = dict(chunk.metadata)
            
            
            metadatas.append(metadata)

            vectors.append(np.asarray(embedding).tolist())

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

        query_args = {
            "query_embeddings": [np.asarray(query_embedding).tolist()],
            "n_results": top_k,
        }
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
    ) -> dict | None:
        if filename is None:
            return None
        return {"filename": str(filename)}

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

    def delete_document_vectors(
        self,
        filename: str,
    ):
        """
        Delete vectors belonging to a specific document.
        """

        where = self._build_where(filename=filename)
        self.collection.delete(where=where)
        logger.info(f"Deleted vectors for document {filename}")

    def get_documents(
        self,
        filename: str | None = None,
    ):
        """
        Return stored chunks, optionally filtered by filename.
        """

        where = self._build_where(filename=filename)
        if where is None:
            return self.collection.get()
        return self.collection.get(where=where)