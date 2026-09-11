"""Small isolated workflow tests; no external database, Chroma, files, or models."""

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
    def get(self): return self
    def to_dict(self): return dict(self.collection.data[self.id])
    def set(self, value): self.collection.data[self.id] = dict(value)
    def update(self, value): self.collection.data[self.id].update(value)
    def delete(self): del self.collection.data[self.id]


class Collection:
    def __init__(self): self.data, self.count = {}, 0
    def document(self, doc_id=None):
        if doc_id is None: self.count += 1; doc_id = f"record-{self.count}"
        return Snapshot(self, doc_id)
    def add(self, value):
        ref = self.document(); ref.set(value); return None, ref
    def where(self, field, _operator, value):
        return type("Query", (), {"stream": lambda query: [Snapshot(self, key) for key, item in self.data.items() if item.get(field) == value]})()


class Database:
    def batch(self):
        pending = []
        return type("Batch", (), {"delete": lambda batch, reference: pending.append(reference), "commit": lambda batch: [reference.delete() for reference in pending]})()


class EndToEndWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.chats, self.messages = Collection(), Collection()
        self.patches = [patch.object(conversation_service, "chats_collection", self.chats), patch.object(conversation_service, "messages_collection", self.messages), patch.object(conversation_service, "db", Database())]
        for patcher in self.patches: patcher.start()
        self.service = ConversationService()

    def tearDown(self):
        for patcher in reversed(self.patches): patcher.stop()

    def test_owned_document_rag_conversation_lifecycle_preserves_historical_source(self):
        # The source is the safe API-shaped result of a selected ready document.
        source = {"document_id": "doc-a", "filename": "schedule.txt", "chunk_index": 0, "distance": 0.2}
        chat_id = self.service.create_chat("user-a", "When is the final presentation?")
        self.service.save_exchange(chat_id, "user-a", "When is the final presentation?", "20 December.", [source])
        self.service.save_exchange(chat_id, "user-a", "When did you say it was?", "20 December.", [source])
        chat, messages = self.service.get_messages(chat_id, "user-a")
        self.assertEqual(chat["message_count"], 4)
        self.assertEqual(messages[-1]["sources"][0]["filename"], "schedule.txt")
        self.assertEqual(len(self.service.recent_history(chat_id, "user-a", 6)), 4)
        self.service.rename_chat(chat_id, "user-a", "Presentation notes")
        self.assertEqual(self.service.get_messages(chat_id, "user-a")[0]["title"], "Presentation notes")

    def test_cross_user_access_and_delete_are_isolated(self):
        first = self.service.create_chat("user-a", "A question")
        second = self.service.create_chat("user-b", "B question")
        self.service.save_exchange(first, "user-a", "q", "a", [])
        self.service.save_exchange(second, "user-b", "q", "a", [])
        with self.assertRaises(ConversationNotFoundError):
            self.service.get_messages(first, "user-b")
        with self.assertRaises(ConversationNotFoundError):
            self.service.delete_chat(first, "user-b")
        self.service.delete_chat(first, "user-a")
        self.assertIn(second, self.chats.data)
        self.assertEqual(len([item for item in self.messages.data.values() if item["chat_id"] == second]), 2)
