"""
firebase_db.py

Firestore client + collection references.
Replaces database/mongodb.py.

Auth (pick ONE, both are supported below):

1) Local dev: set GOOGLE_APPLICATION_CREDENTIALS to the path of a
   service-account JSON file downloaded from
   Firebase Console -> Project Settings -> Service Accounts -> Generate new private key.

2) Deployment (Render/Railway): paste the ENTIRE service-account JSON
   into a single env var FIREBASE_CREDENTIALS_JSON (as a one-line string).
   This avoids needing to upload a file to the host.
"""

import os
import json

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not firebase_admin._apps:
    if FIREBASE_CREDENTIALS_JSON:
        cred_dict = json.loads(FIREBASE_CREDENTIALS_JSON)
        cred = credentials.Certificate(cred_dict)
    elif GOOGLE_APPLICATION_CREDENTIALS:
        cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
    else:
        raise ValueError(
            "No Firebase credentials configured. Set either "
            "FIREBASE_CREDENTIALS_JSON (recommended for deployment) or "
            "GOOGLE_APPLICATION_CREDENTIALS (path to a local JSON key file)."
        )

    firebase_admin.initialize_app(cred)

db = firestore.client()

# ============================================================
# Collection references (mirrors the old Mongo collections)
# ============================================================

users_collection = db.collection("users")
documents_collection = db.collection("documents")
chats_collection = db.collection("chats")
messages_collection = db.collection("messages")
face_embeddings_collection = db.collection("face_embeddings")

print("Firestore connected successfully.")
