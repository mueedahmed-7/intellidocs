"""
retriever.py

Responsible for retrieving the most relevant
document chunks from the vector database.
"""

from dataclasses import dataclass
from typing import Dict, List

from backend.rag.embeddings import EmbeddingManager
from backend.rag.vectorstore import VectorStore
from backend.config import RAG_DISTANCE_THRESHOLD


@dataclass
class RetrievalResult:
    content: str
    document_id: str
    filename: str
    chunk_index: int
    page: int | None
    distance: float


class Retriever:
    """
    Retrieves the most relevant document chunks
    from the vector database.
    """

    def __init__(
        self,
        embedding_manager: EmbeddingManager,
        vector_store: VectorStore,
        distance_threshold: float = RAG_DISTANCE_THRESHOLD
    ):
        """
        Initialize the retriever.

        Args:
            embedding_manager: EmbeddingManager instance.
            vector_store: VectorStore instance.
            distance_threshold: Threshold for considering a document relevant.
        """

        self.embedding_manager = embedding_manager
        self.vector_store = vector_store
        self.distance_threshold = distance_threshold
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        user_id: str | None = None,
        document_ids: list[str] | None = None,
    ) -> List[RetrievalResult]:
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
            user_id=user_id,
            document_ids=document_ids,
        )

        retrieved_chunks: list[RetrievalResult] = []
        seen_content = set()

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]


        # ------------------------------------------------
        # Relevance threshold
        # ------------------------------------------------

        

        for doc, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):

            # Chroma's default metric for this collection is squared L2 distance:
            # lower values are more similar. Embeddings are normalized before storage.
            if distance > self.distance_threshold or not metadata.get("document_id"):
                continue
            if doc in seen_content:
                continue
            seen_content.add(doc)
            retrieved_chunks.append(
                RetrievalResult(
                    content=doc,
                    document_id=str(metadata["document_id"]),
                    filename=metadata.get("original_filename", metadata.get("filename", "Document")),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                    page=metadata.get("page") if isinstance(metadata.get("page"), int) else metadata.get("page_number"),
                    distance=float(distance),
                )
            )
        return retrieved_chunks

    def retrieve_document(
        self,
        filename: str | None = None,
        user_id: str | None = None,
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
            user_id=user_id,
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

    def retrieve_latest_document(
        self,
        user_id: str,
        max_chunks: int = 12,
    ) -> List[Dict]:
        """Return chunks for the authenticated user's most recently uploaded file."""
        results = self.vector_store.get_documents(user_id=user_id)
        metadatas = results.get("metadatas", [])

        if not metadatas:
            return []

        latest_metadata = max(
            metadatas,
            key=lambda metadata: metadata.get("uploaded_at", ""),
        )
        filename = latest_metadata.get("filename")
        if not filename:
            return []

        return self.retrieve_document(
            filename=filename,
            user_id=user_id,
            max_chunks=max_chunks,
        )
