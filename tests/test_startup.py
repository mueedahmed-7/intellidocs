"""Smoke tests that do not contact PostgreSQL, Groq, or local Chroma data."""

import importlib
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-not-for-production")
os.environ["DATABASE_URL"] = "sqlite+pysqlite://"


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
