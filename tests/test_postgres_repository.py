"""Isolated persistence checks for the SQLAlchemy storage adapters."""

import os
import unittest
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite+pysqlite://"

from backend.database.postgres_db import (
    chats_collection,
    documents_collection,
    face_embeddings_collection,
    messages_collection,
    users_collection,
)


class PostgreSQLRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.user_id = str(uuid4())
        users_collection.document(self.user_id).set({
            "name": "Storage Test",
            "email": f"{self.user_id}@example.test",
            "password": "bcrypt-hash",
        })

    def test_document_chat_message_and_face_records_round_trip(self):
        document_id = str(uuid4())
        chat_id = str(uuid4())
        documents_collection.document(document_id).set({
            "user_id": self.user_id,
            "original_filename": "notes.txt",
            "stored_filename": "notes.txt",
            "file_type": "txt",
            "file_size": 12,
            "content_hash": "a" * 64,
            "status": "ready",
            "chunk_count": 1,
        })
        chats_collection.document(chat_id).set({"user_id": self.user_id, "title": "Notes", "message_count": 1})
        messages_collection.add({"user_id": self.user_id, "chat_id": chat_id, "role": "assistant", "content": "Stored answer", "message_order": 1, "sources": [{"document_id": document_id, "page": 1}]})
        face_embeddings_collection.document(self.user_id).set({"user_id": self.user_id, "embedding": [0.1, 0.2, 0.3]})

        self.assertEqual(documents_collection.document(document_id).get().to_dict()["user_id"], self.user_id)
        self.assertEqual(chats_collection.document(chat_id).get().to_dict()["title"], "Notes")
        message = list(messages_collection.where("chat_id", "==", chat_id).stream())[0].to_dict()
        self.assertEqual(message["sources"], [{"document_id": document_id, "page": 1}])
        embedding = face_embeddings_collection.document(self.user_id).get().to_dict()
        self.assertEqual(embedding["embedding"], [0.1, 0.2, 0.3])
        self.assertTrue(embedding["id"])

    def test_email_uniqueness_is_enforced(self):
        email = f"duplicate-{uuid4()}@example.test"
        users_collection.document(str(uuid4())).set({"name": "One", "email": email, "password": "hash"})
        with self.assertRaises(Exception):
            users_collection.document(str(uuid4())).set({"name": "Two", "email": email, "password": "hash"})
