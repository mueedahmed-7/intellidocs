"""Isolated document lifecycle tests using temporary files and in-memory stores."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from fastapi import FastAPI
from fastapi.testclient import TestClient
from langchain_core.documents import Document

with (
    patch("firebase_admin.credentials.Certificate"),
    patch("firebase_admin.initialize_app"),
    patch("firebase_admin.firestore.client"),
    patch("backend.rag.vectorstore.VectorStore"),
):
    from backend.api import routes
    from backend.Services import document_service
    from backend.Services.document_service import DocumentService, DocumentValidationError


class FakeSnapshot:
    def __init__(self, collection, document_id):
        self._collection = collection
        self.id = document_id

    @property
    def exists(self):
        return self.id in self._collection.data

    def to_dict(self):
        return dict(self._collection.data[self.id])

    def get(self):
        return self

    def set(self, data):
        self._collection.data[self.id] = dict(data)

    def update(self, data):
        self._collection.data[self.id].update(data)

    def delete(self):
        del self._collection.data[self.id]


class FakeQuery:
    def __init__(self, collection, field, value):
        self.collection = collection
        self.field = field
        self.value = value

    def stream(self):
        return [
            FakeSnapshot(self.collection, document_id)
            for document_id, data in self.collection.data.items()
            if data.get(self.field) == self.value
        ]


class FakeCollection:
    def __init__(self):
        self.data = {}

    def document(self, document_id):
        return FakeSnapshot(self, document_id)

    def where(self, field, _operator, value):
        return FakeQuery(self, field, value)


class FakeLoader:
    def __init__(self, text="Document text"):
        self.text = text

    def load_document(self, _file_path):
        return [Document(page_content=self.text, metadata={"source": "test"})]


class FakeSplitter:
    def split_documents(self, documents):
        return [
            Document(page_content=f"{document.page_content}-{index}", metadata=dict(document.metadata))
            for document in documents
            for index in range(2)
        ]


class FakeEmbeddings:
    def generate_embeddings(self, chunks):
        return np.zeros((len(chunks), 2), dtype=np.float32)


class FakeVectors:
    def __init__(self):
        self.records = []

    def add_documents(self, chunks, embeddings, ids):
        for chunk, vector_id in zip(chunks, ids):
            self.records.append({"id": vector_id, "metadata": dict(chunk.metadata)})

    def delete_document_vectors(self, user_id, document_id):
        self.records = [
            record
            for record in self.records
            if not (
                record["metadata"].get("user_id") == str(user_id)
                and record["metadata"].get("document_id") == document_id
            )
        ]


class DocumentServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.collection = FakeCollection()
        self.vectors = FakeVectors()
        self.loader = FakeLoader()
        self.service = DocumentService(
            upload_directory=Path(self.temp_directory.name),
            metadata_collection=self.collection,
            document_loader=self.loader,
            document_splitter=FakeSplitter(),
            embeddings=FakeEmbeddings(),
            vectors=self.vectors,
        )

    def tearDown(self):
        self.temp_directory.cleanup()

    def upload(self, filename="notes.txt", content=b"hello world", user_id="user-a"):
        return self.service.ingest_upload(filename, content, user_id)

    def test_valid_txt_creates_safe_metadata_and_chunk_vectors(self):
        document = self.upload()

        self.assertEqual(document["status"], "ready")
        self.assertEqual(document["chunk_count"], 2)
        self.assertNotEqual(document["document_id"], "notes.txt")
        stored = self.collection.data[document["document_id"]]["stored_filename"]
        self.assertEqual(Path(stored).suffix, ".txt")
        self.assertTrue((Path(self.temp_directory.name) / stored).exists())
        self.assertEqual(self.collection.data[document["document_id"]]["user_id"], "user-a")
        self.assertTrue(all(record["metadata"]["document_id"] == document["document_id"] for record in self.vectors.records))
        self.assertTrue(all(record["metadata"]["user_id"] == "user-a" for record in self.vectors.records))
        self.assertEqual([record["metadata"]["chunk_index"] for record in self.vectors.records], [0, 1])

    def test_unsupported_and_oversized_files_are_rejected(self):
        with self.assertRaises(DocumentValidationError):
            self.upload(filename="malware.exe")
        with patch.object(document_service, "MAX_UPLOAD_SIZE_BYTES", 4):
            with self.assertRaises(DocumentValidationError):
                self.upload(content=b"12345")

    def test_empty_text_fails_without_vectors_or_stored_file(self):
        self.service.loader = FakeLoader(text="")
        with self.assertRaises(DocumentValidationError):
            self.upload()

        failed = next(iter(self.collection.data.values()))
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(self.vectors.records, [])
        self.assertEqual(list(Path(self.temp_directory.name).iterdir()), [])

    def test_same_filename_uploads_remain_independent(self):
        first = self.upload()
        second = self.upload()

        self.assertNotEqual(first["document_id"], second["document_id"])
        self.assertEqual(len(self.collection.data), 2)
        self.assertEqual(len(self.vectors.records), 4)

    def test_list_is_owned_by_current_user_only(self):
        self.upload(user_id="user-a")
        self.upload(filename="other.txt", user_id="user-b")

        documents = self.service.list_documents("user-a")
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]["original_filename"], "notes.txt")

    def test_delete_only_removes_owned_document_vectors_and_file(self):
        own_document = self.upload(filename="same.txt", user_id="user-a")
        other_document = self.upload(filename="same.txt", user_id="user-b")

        self.service.delete_document(own_document["document_id"], "user-a")

        self.assertNotIn(own_document["document_id"], self.collection.data)
        self.assertIn(other_document["document_id"], self.collection.data)
        self.assertTrue(all(record["metadata"]["document_id"] != own_document["document_id"] for record in self.vectors.records))
        self.assertTrue(all(record["metadata"]["document_id"] == other_document["document_id"] for record in self.vectors.records))

    def test_other_user_cannot_delete_or_read_document(self):
        document = self.upload(user_id="user-a")

        self.assertIsNone(self.service.get_document(document["document_id"], "user-b"))
        with self.assertRaises(FileNotFoundError):
            self.service.delete_document(document["document_id"], "user-b")
        self.assertIn(document["document_id"], self.collection.data)

    def test_selected_documents_must_be_owned_and_ready(self):
        ready = self.upload(user_id="user-a")
        failed = self.upload(filename="other.txt", user_id="user-b")
        self.collection.data[failed["document_id"]]["status"] = "failed"

        self.assertEqual(
            self.service.ready_document_ids("user-a", [ready["document_id"]]),
            [ready["document_id"]],
        )
        with self.assertRaises(DocumentValidationError):
            self.service.ready_document_ids("user-a", [failed["document_id"]])

    def test_document_api_requires_authentication(self):
        app = FastAPI()
        app.add_api_route("/documents", routes.list_documents, methods=["GET"])

        with TestClient(app) as client:
            response = client.get("/documents")

        self.assertEqual(response.status_code, 401)
