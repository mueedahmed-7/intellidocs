"""Grounded RAG tests with fake embeddings, vectors, and language model."""

import unittest

import numpy as np

from backend.rag.chatengine import ChatEngine
from backend.rag.promptbuilder import PromptBuilder
from backend.rag.reteriver import RetrievalResult, Retriever


class FakeEmbeddings:
    def generate_query_embedding(self, _query):
        return np.array([0.0, 1.0])


class FakeVectorStore:
    def __init__(self, results):
        self.results = results
        self.received = None

    def similarity_search(self, query_embedding, top_k, user_id, document_ids):
        self.received = {"top_k": top_k, "user_id": user_id, "document_ids": document_ids}
        return self.results


class FakeResponse:
    content = "The deadline is 20 December."


class FakeModel:
    def __init__(self):
        self.prompts = []

    def invoke(self, messages):
        self.prompts.append(messages[0].content)
        return FakeResponse()


def chroma_result(items):
    return {
        "documents": [[item[0] for item in items]],
        "metadatas": [[item[1] for item in items]],
        "distances": [[item[2] for item in items]],
    }


class RagTests(unittest.TestCase):
    def test_retrieval_filters_user_and_selected_documents_and_deduplicates(self):
        vectors = FakeVectorStore(chroma_result([
            ("The deadline is 20 December.", {"user_id": "u1", "document_id": "d1", "original_filename": "dates.txt", "chunk_index": 0}, 0.2),
            ("The deadline is 20 December.", {"user_id": "u1", "document_id": "d1", "original_filename": "dates.txt", "chunk_index": 1}, 0.3),
            ("legacy", {"user_id": "u1"}, 0.1),
            ("irrelevant", {"user_id": "u1", "document_id": "d1", "original_filename": "dates.txt", "chunk_index": 2}, 1.7),
        ]))
        retriever = Retriever(FakeEmbeddings(), vectors)

        result = retriever.retrieve("When is the deadline?", top_k=5, user_id="u1", document_ids=["d1"])

        self.assertEqual(vectors.received["user_id"], "u1")
        self.assertEqual(vectors.received["document_ids"], ["d1"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].document_id, "d1")

    def test_retrieval_keeps_relevant_short_form_queries_within_policy_cutoff(self):
        vectors = FakeVectorStore(chroma_result([
            ("Fee Amount: 45,000 PKR. Due Date: 20 September 2026.", {"user_id": "u1", "document_id": "d1", "original_filename": "voucher.pdf", "chunk_index": 0, "page": 1}, 1.54),
            ("unrelated material", {"user_id": "u1", "document_id": "d1", "original_filename": "voucher.pdf", "chunk_index": 1}, 1.7),
        ]))
        result = Retriever(FakeEmbeddings(), vectors).retrieve("What is the due date?", user_id="u1", document_ids=["d1"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].page, 1)

    def test_no_context_returns_controlled_answer_without_model_call(self):
        retriever = Retriever(FakeEmbeddings(), FakeVectorStore(chroma_result([])))
        engine = ChatEngine.__new__(ChatEngine)
        engine.retriever = retriever
        engine.prompt_builder = PromptBuilder()
        engine.llm = FakeModel()

        result = engine.chat("What is the CEO birthday?", user_id="u1", document_ids=["d1"])

        self.assertEqual(result["sources"], [])
        self.assertIn("couldn't find", result["answer"])
        self.assertEqual(engine.llm.prompts, [])

    def test_grounded_answer_returns_safe_sources_and_history_prompt(self):
        source = RetrievalResult(
            content="The project deadline is 20 December.", document_id="d1",
            filename="schedule.txt", chunk_index=3, page=None, distance=0.2,
        )

        class StaticRetriever:
            def retrieve(self, **_kwargs):
                return [source]

        engine = ChatEngine.__new__(ChatEngine)
        engine.retriever = StaticRetriever()
        engine.prompt_builder = PromptBuilder()
        engine.llm = FakeModel()
        result = engine.chat(
            "When is the deadline?", user_id="u1", document_ids=["d1"],
            conversation_history="User: What is the project?\nAssistant: A project.",
        )

        self.assertEqual(result["sources"][0]["document_id"], "d1")
        self.assertEqual(result["sources"][0]["filename"], "schedule.txt")
        self.assertNotIn("file_path", result["sources"][0])
        self.assertIn("RECENT CONVERSATION (not evidence)", engine.llm.prompts[0])
        self.assertIn("DOCUMENT EVIDENCE", engine.llm.prompts[0])
