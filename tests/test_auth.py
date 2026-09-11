"""Authentication tests backed by an in-memory storage replacement."""

import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

os.environ["JWT_SECRET_KEY"] = "test-secret-not-for-production"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["DATABASE_URL"] = "sqlite+pysqlite://"

from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import ExpiredSignatureError, jwt

with (
    patch("backend.rag.vectorstore.VectorStore"),
):
    from backend.api import routes
    from backend.api.schemas import LoginRequest, RegisterRequest
    from backend.Services import auth_service
    from backend.Services.auth_service import AuthService
    from backend.utils.auth_dependency import get_current_user_id
    from backend.utils.jwt_handler import create_access_token, decode_access_token
    from backend.config import JWT_ALGORITHM, JWT_SECRET_KEY


class FakeDocument:
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

    def set(self, value):
        self._collection.data[self.id] = dict(value)


class FakeQuery:
    def __init__(self, collection, field, value):
        self._collection = collection
        self._field = field
        self._value = value

    def limit(self, _count):
        return self

    def stream(self):
        return [
            FakeDocument(self._collection, document_id)
            for document_id, data in self._collection.data.items()
            if data.get(self._field) == self._value
        ]


class FakeUsersCollection:
    def __init__(self):
        self.data = {}
        self._next_id = 1

    def where(self, field, _operator, value):
        return FakeQuery(self, field, value)

    def document(self, document_id=None):
        if document_id is None:
            document_id = f"user-{self._next_id}"
            self._next_id += 1
        return FakeDocument(self, document_id)


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.users = FakeUsersCollection()
        self.collection_patch = patch.object(auth_service, "users_collection", self.users)
        self.collection_patch.start()

    def tearDown(self):
        self.collection_patch.stop()

    def register(self, email="student@example.com", password="correct-password"):
        return routes.register(
            RegisterRequest(name="Student Name", email=email, password=password)
        )

    def test_registration_returns_safe_profile_and_token(self):
        response = self.register()

        self.assertEqual(response.user.email, "student@example.com")
        self.assertEqual(response.user.name, "Student Name")
        self.assertTrue(response.access_token)
        self.assertNotIn("password", response.user.model_dump())

    def test_duplicate_registration_is_rejected(self):
        self.register()

        with self.assertRaises(Exception) as context:
            self.register()

        self.assertEqual(context.exception.status_code, 409)

    def test_login_success_returns_safe_profile(self):
        self.register()
        response = routes.login(LoginRequest(email="STUDENT@EXAMPLE.COM", password="correct-password"))

        self.assertEqual(response.user.email, "student@example.com")
        self.assertNotIn("password", response.user.model_dump())

    def test_wrong_password_is_rejected(self):
        self.register()

        with self.assertRaises(Exception) as context:
            routes.login(LoginRequest(email="student@example.com", password="wrong-password"))

        self.assertEqual(context.exception.status_code, 401)

    def test_unknown_user_is_rejected(self):
        with self.assertRaises(Exception) as context:
            routes.login(LoginRequest(email="unknown@example.com", password="wrong-password"))

        self.assertEqual(context.exception.status_code, 401)

    def test_email_is_normalized(self):
        response = self.register(email="  Student@Example.COM  ")
        self.assertEqual(response.user.email, "student@example.com")

    def test_jwt_creation_and_subject_validation(self):
        token = create_access_token("user-123")
        self.assertEqual(decode_access_token(token), "user-123")

    def test_expired_jwt_is_rejected(self):
        expired_token = jwt.encode(
            {"sub": "user-123", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

        with self.assertRaises(ExpiredSignatureError):
            decode_access_token(expired_token)

    def test_missing_and_invalid_tokens_are_rejected(self):
        with self.assertRaises(Exception) as missing:
            get_current_user_id(None)
        with self.assertRaises(Exception) as invalid:
            get_current_user_id("Bearer malformed-token")

        self.assertEqual(missing.exception.status_code, 401)
        self.assertEqual(invalid.exception.status_code, 401)

    def test_auth_me_returns_profile_for_valid_token(self):
        registered = self.register()
        app = FastAPI()
        app.add_api_route("/auth/me", routes.get_current_user, methods=["GET"])

        with TestClient(app) as client:
            response = client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {registered.access_token}"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "student@example.com")
        self.assertNotIn("password", response.json())

    def test_auth_me_rejects_invalid_token(self):
        app = FastAPI()
        app.add_api_route("/auth/me", routes.get_current_user, methods=["GET"])

        with TestClient(app) as client:
            response = client.get("/auth/me", headers={"Authorization": "Bearer malformed"})

        self.assertEqual(response.status_code, 401)
