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

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

from backend.config import ENV_FILE, PROJECT_ROOT
from backend.database.firebase_config import resolve_firebase_credential

load_dotenv(ENV_FILE)

if not firebase_admin._apps:
    cred = resolve_firebase_credential(credentials.Certificate, project_root=PROJECT_ROOT)
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
documents_collection = db.collection("documents")
