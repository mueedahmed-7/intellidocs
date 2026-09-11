"""Smoke tests that do not contact Firestore, Groq, or local Chroma data."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


class StartupSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Import low-level modules first so their runtime constructors can be
        # replaced before backend.services creates application singletons.
        import backend.rag.chatengine
        import backend.rag.vectorstore

        for module_name in list(sys.modules):
            if module_name in {"backend.main", "backend.services", "backend.api.routes"}:
                sys.modules.pop(module_name)

        with (
            patch("firebase_admin.credentials.Certificate"),
            patch("firebase_admin.initialize_app"),
            patch("firebase_admin.firestore.client", return_value=MagicMock()),
            patch("backend.rag.vectorstore.VectorStore"),
            patch("backend.rag.chatengine.ChatEngine"),
        ):
            cls.main = importlib.import_module("backend.main")

    def test_fastapi_app_is_importable_from_project_root(self):
        self.assertEqual(self.main.app.title, "AI RAG Chatbot API")

    def test_health_endpoint(self):
        with TestClient(self.main.app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
