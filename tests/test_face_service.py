"""Face web-path tests with fake Firestore and embeddings; no camera or model needed."""

import unittest
from unittest.mock import patch

import numpy as np

from backend.Services import face_service
from backend.Services.face_service import FaceService, FaceValidationError


class Snapshot:
    def __init__(self, collection, key): self.collection, self.key = collection, key
    @property
    def exists(self): return self.key in self.collection.data
    def to_dict(self): return dict(self.collection.data[self.key])
    def get(self): return self
    def set(self, value): self.collection.data[self.key] = dict(value)


class Collection:
    def __init__(self, data=None): self.data = data or {}
    def document(self, key): return Snapshot(self, key)
    def stream(self): return [Snapshot(self, key) for key in self.data]


class FaceServiceTests(unittest.TestCase):
    def setUp(self):
        self.users = Collection({"u1": {"name": "Student", "email": "student@example.com"}})
        self.faces = Collection()
        self.patches = [
            patch.object(face_service, "users_collection", self.users),
            patch.object(face_service, "face_embeddings_collection", self.faces),
            patch.object(face_service, "detect_and_embed_from_image", return_value=(np.array([1.0, 0.0], dtype=np.float32), None)),
        ]
        for item in self.patches: item.start()

    def tearDown(self):
        for item in reversed(self.patches): item.stop()

    def test_registration_uses_authenticated_user_id_only(self):
        FaceService.register_face("u1", b"image")
        self.assertEqual(self.faces.data["u1"]["user_id"], "u1")
        self.assertNotIn("username", self.faces.data["u1"])

    def test_empty_image_and_detector_errors_are_validation_errors(self):
        with self.assertRaises(FaceValidationError): FaceService.register_face("u1", b"")
        with patch.object(face_service, "detect_and_embed_from_image", return_value=(None, "No face detected. Please try again.")):
            with self.assertRaises(FaceValidationError): FaceService.login_with_face(b"image")

    def test_login_skips_malformed_embeddings_and_returns_safe_user(self):
        self.faces.data.update({
            "bad": {"user_id": "bad", "embedding": ["not-a-number"]},
            "u1": {"user_id": "u1", "embedding": [1.0, 0.0]},
        })
        result = FaceService.login_with_face(b"image")
        self.assertTrue(result["success"])
        self.assertEqual(result["user_id"], "u1")
        self.assertNotIn("embedding", result)

    def test_no_matching_face_is_not_authenticated(self):
        self.faces.data["u1"] = {"user_id": "u1", "embedding": [0.0, 1.0]}
        result = FaceService.login_with_face(b"image")
        self.assertFalse(result["success"])

