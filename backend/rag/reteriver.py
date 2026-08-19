"""
retriever.py

Responsible for retrieving the most relevant
document chunks from the vector database.
"""

from typing import List, Dict

from rag.embeddings import EmbeddingManager
from rag.vectorstore import VectorStore


class Retriever:
    """
    Retrieves the most relevant document chunks
    from the vector database.
    """

    def __init__(
        self,
        embedding_manager: EmbeddingManager,
        vector_store: VectorStore,
    ):
        """
        Initialize the retriever.

        Args:
            embedding_manager: EmbeddingManager instance.
            vector_store: VectorStore instance.
        """

        self.embedding_manager = embedding_manager
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict]:
        """
        Retrieve the most relevant document chunks.

        Results with a distance greater than the relevance
        threshold are discarded.
        """

        if not query.strip():
            return []

        # Generate embedding for the user query
        query_embedding = self.embedding_manager.generate_query_embedding(
            query
        )

        # Search ChromaDB
        results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        retrieved_chunks = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        # Temporary: inspect distances during testing
        print("RETRIEVAL RESULTS:")

        for doc, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            print(
                f"Distance: {distance} | "
                f"File: {metadata.get('filename')} | "
                f"Page: {metadata.get('page')}"
            )

        # ------------------------------------------------
        # Relevance threshold
        # ------------------------------------------------

        DISTANCE_THRESHOLD = 1.5

        for doc, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):

            if distance > DISTANCE_THRESHOLD:
                continue

            retrieved_chunks.append(
                {
                    "content": doc,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return retrieved_chunks

    def retrieve_document(
        self,
        filename: str | None = None,
        max_chunks: int = 20,
    ):
        """
        Retrieve the first N chunks of a document for
        document-level tasks like summarization.
        """
        if not isinstance(max_chunks, int) or max_chunks < 1:
            raise ValueError("max_chunks must be a positive integer.")

        results = self.vector_store.get_documents(
            filename=filename,
        )

        retrieved_chunks = []

        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])

        # Limit the number of chunks
        documents = documents[:max_chunks]
        metadatas = metadatas[:max_chunks]

        for doc, metadata in zip(documents, metadatas):

            retrieved_chunks.append(
                {
                    "content": doc,
                    "metadata": metadata,
                    "distance": 0,
                }
            )

        return retrieved_chunks