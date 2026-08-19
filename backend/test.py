from rag.loader import DocumentLoader
from rag.splitter import DocumentSplitter

from pathlib import Path

files_dir = Path.cwd() / "files"
pdf_files = list(files_dir.glob("*.pdf"))
if not pdf_files:
	raise FileNotFoundError(f"No PDF found in {files_dir.resolve()}")

doc = DocumentLoader().load_document(str(pdf_files[0]))

print(len(doc))

splitter = DocumentSplitter()
chunks = splitter.split_documents(doc)

print(f"Number of chunks: {len(chunks)}")
print(chunks)

from rag.embeddings import EmbeddingManager

embedding_manager = EmbeddingManager()
embeddings = embedding_manager.generate_embeddings(chunks)

print(len(embeddings))
print(embeddings)

from rag.vectorstore import VectorStore

store = VectorStore()
store.add_documents(chunks, embeddings)

print(f"Stored chunks: {store.count()}")

query = "What is ML?"
print(f"Query: {query}")

from rag.reteriver import Retriever

retriever = Retriever(embedding_manager, store)
results = retriever.retrieve(query, top_k=3)
print(f"Retrieved results: {results}")
