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

vector_store = VectorStore()

retriever = Retriever(embedding_manager, vector_store)

prompt_builder = PromptBuilder()

_chat_engine = None


def get_chat_engine() -> ChatEngine:
    """Create the Groq client only when a chat request actually needs it."""
    global _chat_engine

    if _chat_engine is None:
        _chat_engine = ChatEngine(
            retriever=retriever,
            prompt_builder=prompt_builder,
            api_key=groq_api_key(),
        )
    return _chat_engine
