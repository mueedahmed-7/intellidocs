"""SQLAlchemy models for IntelliDocs persistent application state."""
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON

class Base(DeclarativeBase): pass
def uid(): return str(uuid4())
def timestamp(): return datetime.now(timezone.utc).isoformat()

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=uid)
    name = Column(String(200), nullable=False); email = Column(String(320), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False); created_at = Column(String(40), default=timestamp); updated_at = Column(String(40), default=timestamp, onupdate=timestamp)
class StoredDocument(Base):
    __tablename__ = "documents"
    document_id = Column(String(36), primary_key=True); user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    original_filename = Column(String(512), nullable=False); stored_filename = Column(String(512)); file_type = Column(String(20)); file_size = Column(Integer); content_hash = Column(String(64)); status = Column(String(20), index=True); created_at = Column(String(40), default=timestamp); updated_at = Column(String(40), default=timestamp, onupdate=timestamp); chunk_count = Column(Integer, default=0); processing_error = Column(Text)
class Chat(Base):
    __tablename__ = "chats"
    chat_id = Column(String(36), primary_key=True, default=uid); user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200)); created_at = Column(String(40), default=timestamp); updated_at = Column(String(40), default=timestamp, onupdate=timestamp, index=True); message_count = Column(Integer, default=0)
class Message(Base):
    __tablename__ = "messages"
    id = Column(String(36), primary_key=True, default=uid); chat_id = Column(String(36), ForeignKey("chats.chat_id", ondelete="CASCADE"), nullable=False, index=True); user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(20)); content = Column(Text); created_at = Column(String(40), default=timestamp); message_order = Column(Integer, default=0); sources = Column(JSON, default=list)
class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"
    id = Column(String(36), primary_key=True, default=uid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    embedding = Column(JSON, nullable=False); created_at = Column(String(40), default=timestamp); updated_at = Column(String(40), default=timestamp, onupdate=timestamp)
