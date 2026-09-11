"""Hybrid general AI and strict document-RAG routing tests with no Groq calls."""

import unittest

from backend.rag.chatengine import ChatEngine
from backend.rag.promptbuilder import PromptBuilder
from backend.rag.reteriver import RetrievalResult


class Response:
    content = "A helpful general answer."


class Model:
    def __init__(self): self.prompts = []
    def invoke(self, messages): self.prompts.append(messages[0].content); return Response()


class EmptyRetriever:
    def __init__(self): self.calls = []
    def retrieve(self, **kwargs): self.calls.append(kwargs); return []


class HybridChatTests(unittest.TestCase):
    def engine(self, retriever):
        engine = ChatEngine.__new__(ChatEngine)
        engine.retriever, engine.prompt_builder, engine.llm = retriever, PromptBuilder(), Model()
        return engine

    def test_generic_question_without_documents_uses_llm_and_has_no_sources(self):
        engine = self.engine(EmptyRetriever())
        result = engine.chat("What is artificial intelligence?", document_ids=[], document_mode=False)
        self.assertEqual(result["sources"], [])
        self.assertEqual(len(engine.llm.prompts), 1)
        self.assertIn("general-purpose AI assistant", engine.llm.prompts[0])
        self.assertEqual(engine.retriever.calls, [])

    def test_explicit_document_question_without_evidence_never_falls_back_to_general_ai(self):
        engine = self.engine(EmptyRetriever())
        result = engine.chat("According to my PDF, what is the deadline?", user_id="u1", document_ids=["d1"], document_mode=True)
        self.assertIn("selected documents", result["answer"])
        self.assertEqual(result["sources"], [])
        self.assertEqual(engine.llm.prompts, [])
        self.assertEqual(engine.retriever.calls[0]["document_ids"], ["d1"])

    def test_document_mode_returns_sources_and_generic_followup_stays_generic_after_new_chat(self):
        source = RetrievalResult("Deadline is 20 December.", "d1", "schedule.pdf", 0, 1, 0.2)
        class Retriever:
            def retrieve(self, **_kwargs): return [source]
        engine = self.engine(Retriever())
        document_result = engine.chat("What is the deadline in this document?", user_id="u1", document_ids=["d1"], document_mode=True)
        generic_result = engine.chat("Explain it like I am 10.", document_ids=[], conversation_history="User: What is machine learning?", document_mode=False)
        self.assertEqual(document_result["sources"][0]["document_id"], "d1")
        self.assertEqual(generic_result["sources"], [])
        self.assertIn("RECENT CONVERSATION", engine.llm.prompts[-1])

    def test_document_intent_detection_covers_selection_language(self):
        self.assertTrue(ChatEngine.is_explicit_document_request("Summarize my uploaded report."))
        self.assertTrue(ChatEngine.is_explicit_document_request("What does this voucher say?"))
        self.assertFalse(ChatEngine.is_explicit_document_request("What is machine learning?"))

    def test_selected_voucher_switches_from_rag_to_generic_without_retrieval(self):
        source = RetrievalResult("Voucher number is 1629003.", "voucher-id", "voucher.pdf", 0, 1, 0.2)
        class Retriever:
            def __init__(self): self.calls = []
            def retrieve(self, **kwargs): self.calls.append(kwargs); return [source]
        retriever = Retriever()
        engine = self.engine(retriever)
        selected = ["voucher-id"]

        first_mode = ChatEngine.should_use_document_mode("what is the voucher number", True, [])
        first = engine.chat("what is the voucher number", user_id="u1", document_ids=selected, document_mode=first_mode)
        history = [
            {"role": "user", "content": "what is the voucher number", "sources": []},
            {"role": "assistant", "content": first["answer"], "sources": first["sources"]},
        ]
        second_mode = ChatEngine.should_use_document_mode("what is AI", True, history)
        second = engine.chat("what is AI", user_id="u1", document_ids=selected, document_mode=second_mode)

        self.assertTrue(first_mode)
        self.assertEqual(first["sources"][0]["document_id"], "voucher-id")
        self.assertFalse(second_mode)
        self.assertEqual(second["sources"], [])
        self.assertEqual(len(retriever.calls), 1)
        self.assertIn("general-purpose AI assistant", engine.llm.prompts[-1])

    def test_selected_voucher_switches_from_generic_to_rag(self):
        source = RetrievalResult("Due date is 20 December.", "voucher-id", "voucher.pdf", 0, 1, 0.2)
        class Retriever:
            def retrieve(self, **_kwargs): return [source]
        engine = self.engine(Retriever())
        selected = ["voucher-id"]

        generic_mode = ChatEngine.should_use_document_mode("What is AI?", True, [])
        generic = engine.chat("What is AI?", document_ids=selected, document_mode=generic_mode)
        rag_mode = ChatEngine.should_use_document_mode("What is the due date on my voucher?", True, [])
        rag = engine.chat("What is the due date on my voucher?", user_id="u1", document_ids=selected, document_mode=rag_mode)

        self.assertFalse(generic_mode)
        self.assertEqual(generic["sources"], [])
        self.assertTrue(rag_mode)
        self.assertEqual(rag["sources"][0]["document_id"], "voucher-id")

    def test_sourced_turn_only_enables_a_real_document_follow_up(self):
        history = [{"role": "assistant", "content": "Voucher number is 1629003.", "sources": [{"document_id": "voucher-id"}]}]
        self.assertTrue(ChatEngine.should_use_document_mode("When is it due?", True, history))
        self.assertFalse(ChatEngine.should_use_document_mode("Explain AI like I am 10.", True, history))
        generic_history = history + [{"role": "assistant", "content": "AI is a field of computing.", "sources": []}]
        self.assertFalse(ChatEngine.should_use_document_mode("And what about it?", True, generic_history))
