# """
# face_service.py

# Stores/reads face embeddings in Firestore instead of local .npy files
# (local files don't survive redeploys/restarts on Render/Railway, since
# the filesystem there is ephemeral).

# Embeddings are stored as plain lists of floats inside each user's
# Firestore document.
# """

# import numpy as np

# from database.firebase_db import face_embeddings_collection
# from member3.face.face_utils import detect_and_embed_from_image
# from member3.face.config import MATCH_COSINE_THRESHOLD
# from member3.face.face_utils import compute_cosine_similarity


# class FaceService:

#     @staticmethod
#     def register_face(username: str, image_bytes: bytes):
#         """
#         Detect a face in the given image and store its embedding
#         under the given username in Firestore.
#         """
#         embedding, error = detect_and_embed_from_image(None, image_bytes)

#         if error:
#             raise ValueError(error)

#         face_embeddings_collection.document(username).set(
#             {
#                 "username": username,
#                 "embedding": embedding.astype(float).tolist(),
#             }
#         )

#         return {
#             "success": True,
#             "username": username,
#         }

#     @staticmethod
#     def login_with_face(image_bytes: bytes):
#         """
#         Detect a face in the given image and compare it against every
#         registered embedding in Firestore. Returns the best match if
#         it clears the similarity threshold.
#         """
#         embedding, error = detect_and_embed_from_image(None, image_bytes)

#         if error:
#             raise ValueError(error)

#         docs = list(face_embeddings_collection.stream())

#         if not docs:
#             raise ValueError("No registered faces found.")

#         best_user = None
#         best_similarity = -1.0

#         for doc in docs:
#             data = doc.to_dict()
#             stored_embedding = np.array(data["embedding"], dtype=np.float32)

#             similarity = compute_cosine_similarity(embedding, stored_embedding)

#             if similarity > best_similarity:
#                 best_similarity = similarity
#                 best_user = data["username"]

#         if best_user is not None and best_similarity >= MATCH_COSINE_THRESHOLD:
#             return {
#                 "success": True,
#                 "username": best_user,
#                 "similarity": float(best_similarity),
#             }

#         return {
#             "success": False,
#             "similarity": float(best_similarity),
#             "message": "Face not recognized.",
#         }
"""
face_service.py

Stores/reads face embeddings in Firestore, keyed by the real Firestore
user_id (not a free-typed username) so that a successful face match
maps directly back to a `users` account.
"""

import numpy as np

from database.firebase_db import face_embeddings_collection, users_collection
from member3.face.face_utils import detect_and_embed_from_image
from member3.face.config import MATCH_COSINE_THRESHOLD
from member3.face.face_utils import compute_cosine_similarity


class FaceService:

    @staticmethod
    def register_face(user_id: str, image_bytes: bytes):
        """
        Detect a face in the given image and store its embedding
        under the given (already-authenticated) user_id in Firestore.
        """
        user_doc = users_collection.document(user_id).get()
        if not user_doc.exists:
            raise ValueError("User account not found.")

        embedding, error = detect_and_embed_from_image(None, image_bytes)

        if error:
            raise ValueError(error)

        face_embeddings_collection.document(user_id).set(
            {
                "user_id": user_id,
                "embedding": embedding.astype(float).tolist(),
            }
        )

        return {
            "success": True,
            "user_id": user_id,
        }

    @staticmethod
    def login_with_face(image_bytes: bytes):
        """
        Detect a face in the given image and compare it against every
        registered embedding in Firestore. Returns the matched user's
        id/name/email if it clears the similarity threshold.
        """
        embedding, error = detect_and_embed_from_image(None, image_bytes)

        if error:
            raise ValueError(error)

        docs = list(face_embeddings_collection.stream())

        if not docs:
            raise ValueError("No registered faces found.")

        best_user_id = None
        best_similarity = -1.0

        for doc in docs:
            data = doc.to_dict()
            stored_embedding = np.array(data["embedding"], dtype=np.float32)

            similarity = compute_cosine_similarity(embedding, stored_embedding)

            if similarity > best_similarity:
                best_similarity = similarity
                best_user_id = data["user_id"]

        if best_user_id is not None and best_similarity >= MATCH_COSINE_THRESHOLD:
            user_doc = users_collection.document(best_user_id).get()

            if not user_doc.exists:
                return {
                    "success": False,
                    "message": "Matched face has no linked account.",
                }

            user = user_doc.to_dict()

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