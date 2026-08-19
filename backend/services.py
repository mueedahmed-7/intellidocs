from rag.loader import DocumentLoader
from rag.splitter import DocumentSplitter
from rag.embeddings import EmbeddingManager
from rag.vectorstore import VectorStore
from rag.reteriver import Retriever
from rag.promptbuilder import PromptBuilder
from rag.chatengine import ChatEngine
import os
from dotenv import load_dotenv

load_dotenv()


loader = DocumentLoader()

splitter = DocumentSplitter()

embedding_manager = EmbeddingManager()

vector_store = VectorStore()

retriever = Retriever(embedding_manager, vector_store)

prompt_builder = PromptBuilder()

chat_engine = ChatEngine(
    retriever=retriever,
    prompt_builder=prompt_builder,
    api_key=os.getenv("GROQ_API_KEY"),
)