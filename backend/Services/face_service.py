"""
face_service.py

Stores/reads face embeddings in PostgreSQL, keyed by the real application
user_id (not a free-typed username) so that a successful face match
maps directly back to a `users` account.
"""

import numpy as np

from backend.database.postgres_db import face_embeddings_collection, users_collection
from member3.face.face_utils import detect_and_embed_from_image
from member3.face.config import MATCH_COSINE_THRESHOLD
from member3.face.face_utils import compute_cosine_similarity


class FaceValidationError(ValueError):
    """A user-correctable capture or biometric-record error."""


class FaceStorageError(Exception):
    """Persistent storage is unavailable or could not safely persist face data."""


class FaceService:

    @staticmethod
    def register_face(user_id: str, image_bytes: bytes):
        """
        Detect a face in the given image and store its embedding
        under the given (already-authenticated) user_id in PostgreSQL.
        """
        if not image_bytes:
            raise FaceValidationError("Invalid image.")
        try:
            user_doc = users_collection.document(user_id).get()
        except Exception as error:
            raise FaceStorageError("Face storage is unavailable.") from error
        if not user_doc.exists:
            raise FaceValidationError("User account not found.")

        embedding, error = detect_and_embed_from_image(None, image_bytes)

        if error:
            raise FaceValidationError(error)

        try:
            face_embeddings_collection.document(user_id).set(
                {"user_id": user_id, "embedding": embedding.astype(float).tolist()}
            )
        except Exception as error:
            raise FaceStorageError("Face storage is unavailable.") from error

        return {
            "success": True,
            "user_id": user_id,
        }

    @staticmethod
    def login_with_face(image_bytes: bytes):
        """
        Detect a face in the given image and compare it against every
        registered embedding in PostgreSQL. Returns the matched user's
        id/name/email if it clears the similarity threshold.
        """
        if not image_bytes:
            raise FaceValidationError("Invalid image.")
        embedding, error = detect_and_embed_from_image(None, image_bytes)

        if error:
            raise FaceValidationError(error)

        try:
            docs = list(face_embeddings_collection.stream())
        except Exception as error:
            raise FaceStorageError("Face storage is unavailable.") from error

        if not docs:
            raise FaceValidationError("No registered faces found.")

        best_user_id = None
        best_similarity = -1.0

        for doc in docs:
            data = doc.to_dict() or {}
            stored_user_id = data.get("user_id")
            try:
                stored_embedding = np.asarray(data.get("embedding"), dtype=np.float32).reshape(-1)
            except (TypeError, ValueError):
                continue
            if not stored_user_id or stored_embedding.shape != embedding.shape or not np.isfinite(stored_embedding).all():
                continue

            similarity = compute_cosine_similarity(embedding, stored_embedding)

            if similarity > best_similarity:
                best_similarity = similarity
                best_user_id = stored_user_id

        if best_user_id is not None and best_similarity >= MATCH_COSINE_THRESHOLD:
            try:
                user_doc = users_collection.document(best_user_id).get()
            except Exception as error:
                raise FaceStorageError("Face storage is unavailable.") from error

            if not user_doc.exists:
                return {
                    "success": False,
                    "message": "Matched face has no linked account.",
                }

            user = user_doc.to_dict() or {}
            if not user.get("name") or not user.get("email"):
                return {"success": False, "message": "Matched face has an invalid account record."}

            return {
                "success": True,
                "user_id": best_user_id,
                "name": user["name"],
                "email": user["email"],
                "similarity": float(best_similarity),
            }

        return {
            "success": False,
            "similarity": float(best_similarity),
            "message": "Face not recognized.",
        }
