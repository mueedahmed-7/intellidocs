from backend.rag.loader import DocumentLoader
from backend.rag.splitter import DocumentSplitter
from backend.rag.embeddings import EmbeddingManager
from backend.rag.vectorstore import VectorStore
from backend.rag.reteriver import Retriever
from backend.rag.promptbuilder import PromptBuilder
from backend.rag.chatengine import ChatEngine
from backend.config import groq_api_key


loader = DocumentLoader()
splitter = DocumentSplitter()
embedding_manager = EmbeddingManager()
prompt_builder = PromptBuilder()
_vector_store = _retriever = _chat_engine = None


def get_vector_store() -> VectorStore:
    """Open local Chroma only when a document or RAG query needs it."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever(embedding_manager, get_vector_store())
    return _retriever


def get_chat_engine() -> ChatEngine:
    """Create the Groq client only when a chat request actually needs it."""
    global _chat_engine

    if _chat_engine is None:
        _chat_engine = ChatEngine(
            retriever=get_retriever(),
            prompt_builder=prompt_builder,
            api_key=groq_api_key(),
        )
    return _chat_engine
