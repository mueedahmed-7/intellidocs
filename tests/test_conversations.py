"""Isolated Phase 6 conversation lifecycle tests."""

import unittest
from unittest.mock import patch

from backend.Services import conversation_service
from backend.Services.conversation_service import ConversationNotFoundError, ConversationService


class Snapshot:
    def __init__(self, collection, doc_id): self.collection, self.id = collection, doc_id
    @property
    def exists(self): return self.id in self.collection.data
    @property
    def reference(self): return self
    def to_dict(self): return dict(self.collection.data[self.id])
    def get(self): return self
    def set(self, value): self.collection.data[self.id] = dict(value)
    def update(self, value): self.collection.data[self.id].update(value)
    def delete(self): del self.collection.data[self.id]


class Query:
    def __init__(self, collection, field, value): self.collection, self.field, self.value = collection, field, value
    def stream(self): return [Snapshot(self.collection, key) for key, value in self.collection.data.items() if value.get(self.field) == self.value]


class Collection:
    def __init__(self): self.data, self.counter = {}, 0
    def document(self, doc_id=None):
        if doc_id is None:
            self.counter += 1
            doc_id = f"id-{self.counter}"
        return Snapshot(self, doc_id)
    def add(self, value):
        ref = self.document(); ref.set(value); return None, ref
    def where(self, field, _operator, value): return Query(self, field, value)


class Batch:
    def __init__(self): self.deletes = []
    def delete(self, reference): self.deletes.append(reference)
    def commit(self):
        for reference in self.deletes: reference.delete()


class Database:
    def batch(self): return Batch()


class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.chats, self.messages = Collection(), Collection()
        self.patches = [
            patch.object(conversation_service, "chats_collection", self.chats),
            patch.object(conversation_service, "messages_collection", self.messages),
            patch.object(conversation_service, "db", Database()),
        ]
        for item in self.patches: item.start()
        self.service = ConversationService()

    def tearDown(self):
        for item in reversed(self.patches): item.stop()

    def test_first_question_creates_titled_chat_and_exchange(self):
        chat_id = self.service.create_chat("u1", "  What are the findings in this paper?  ")
        self.service.save_exchange(chat_id, "u1", "What are the findings in this paper?", "They are grounded.", [])
        chat, messages = self.service.get_messages(chat_id, "u1")
        self.assertEqual(chat["title"], "What are the findings in this paper?")
        self.assertEqual(chat["message_count"], 2)
        self.assertEqual([item["role"] for item in messages], ["user", "assistant"])

    def test_list_is_owned_sorted_and_legacy_title_is_safe(self):
        first = self.service.create_chat("u1", "First")
        second = self.service.create_chat("u1", "Second")
        self.chats.data[first]["updated_at"] = "2025-01-01T00:00:00+00:00"
        self.chats.data[second]["updated_at"] = "2025-02-01T00:00:00+00:00"
        self.chats.document("other").set({"user_id": "u2", "title": "Private", "created_at": "", "updated_at": "9999"})
        self.chats.data[first]["title"] = ""
        chats = self.service.list_chats("u1")
        self.assertEqual([chat["chat_id"] for chat in chats], [second, first])
        self.assertEqual(chats[1]["title"], "New Conversation")

    def test_wrong_user_cannot_open_rename_delete_or_continue(self):
        chat_id = self.service.create_chat("u1", "Private")
        for operation in (
            lambda: self.service.get_messages(chat_id, "u2"),
            lambda: self.service.rename_chat(chat_id, "u2", "No"),
            lambda: self.service.delete_chat(chat_id, "u2"),
            lambda: self.service.save_exchange(chat_id, "u2", "No", "No", []),
        ):
            with self.assertRaises(ConversationNotFoundError): operation()

    def test_rename_and_delete_clean_only_owned_chat_messages(self):
        first, second = self.service.create_chat("u1", "First"), self.service.create_chat("u1", "Second")
        self.service.save_exchange(first, "u1", "q1", "a1", [])
        self.service.save_exchange(second, "u1", "q2", "a2", [])
        renamed = self.service.rename_chat(first, "u1", "Research Notes")
        self.assertEqual(renamed["title"], "Research Notes")
        self.service.delete_chat(first, "u1")
        self.assertNotIn(first, self.chats.data)
        self.assertEqual(len([item for item in self.messages.data.values() if item["chat_id"] == first]), 0)
        self.assertEqual(len([item for item in self.messages.data.values() if item["chat_id"] == second]), 2)

    def test_legacy_combined_records_and_sources_normalize_for_history(self):
        self.messages.document("legacy").set({"user_id": "u1", "question": "Old question", "answer": "Old answer", "sources": [{"document_id": "gone", "filename": "deleted.pdf", "chunk_index": 0, "distance": 0.1}], "created_at": "2025-01-01"})
        chat, messages = self.service.get_messages("legacy-history", "u1")
        self.assertEqual(chat["title"], "Earlier chat history")
        assistant = next(item for item in messages if item["role"] == "assistant")
        self.assertEqual(assistant["sources"][0]["filename"], "deleted.pdf")

    def test_recent_history_is_bounded_to_the_current_chat(self):
        first, second = self.service.create_chat("u1", "One"), self.service.create_chat("u1", "Two")
        for number in range(4): self.service.save_exchange(first, "u1", f"q{number}", f"a{number}", [])
        self.service.save_exchange(second, "u1", "other", "other", [])
        history = self.service.recent_history(first, "u1", limit=6)
        self.assertEqual(len(history), 6)
        self.assertNotIn("other", [item["content"] for item in history])
