"""Document ingestion, metadata, and cleanup lifecycle."""

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

from backend.config import MAX_UPLOAD_SIZE_BYTES, UPLOAD_DIR
from backend.database.postgres_db import documents_collection
from backend.services import embedding_manager, get_vector_store, loader, splitter


class DocumentValidationError(ValueError):
    """Raised for client-correctable document input failures."""

class DocumentTooLargeError(DocumentValidationError):
    """Raised when an upload exceeds the configured maximum size."""



class DocumentStorageError(RuntimeError):
    """Raised when persistent storage, vectors, or file cleanup cannot complete."""


class DocumentService:
    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

    def __init__(
        self,
        upload_directory: str | Path = UPLOAD_DIR,
        metadata_collection=None,
        document_loader=None,
        document_splitter=None,
        embeddings=None,
        vectors=None,
    ):
        self.upload_directory = Path(upload_directory)
        self.upload_directory.mkdir(parents=True, exist_ok=True)
        self.metadata_collection = metadata_collection or documents_collection
        self.loader = document_loader or loader
        self.splitter = document_splitter or splitter
        self.embedding_manager = embeddings or embedding_manager
        self._vector_store = vectors

    @property
    def vector_store(self):
        """Delay Chroma opening until ingestion, retrieval, or deletion needs it."""
        if self._vector_store is None:
            self._vector_store = get_vector_store()
        return self._vector_store

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _safe_error(error: Exception) -> str:
        if isinstance(error, DocumentValidationError):
            return str(error)
        return "Document processing failed. Please verify that the file is readable."

    @staticmethod
    def _display_metadata(document_id: str, data: dict) -> dict:
        return {
            "document_id": document_id,
            "original_filename": data["original_filename"],
            "file_type": data["file_type"],
            "file_size": data["file_size"],
            "status": data["status"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
            "chunk_count": data.get("chunk_count", 0),
            "processing_error": data.get("processing_error"),
        }

    def _validate_upload(
        self,
        filename: str | None,
        content: bytes,
        content_type: str | None,
    ) -> tuple[str, str]:
        if not filename or Path(filename).name != filename:
            raise DocumentValidationError("Invalid filename.")

        suffix = Path(filename).suffix.lower()
        if suffix not in self.ALLOWED_EXTENSIONS:
            raise DocumentValidationError("Unsupported file type. Use PDF, DOCX, TXT, or Markdown.")
        expected_types = {
            ".pdf": {"application/pdf"},
            ".docx": {
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            },
            ".txt": {"text/plain"},
            ".md": {"text/markdown", "text/plain"},
        }
        if content_type and content_type not in {"application/octet-stream", *expected_types[suffix]}:
            raise DocumentValidationError("The file content type does not match its extension.")
        if not content:
            raise DocumentValidationError("The uploaded file is empty.")
        if len(content) > MAX_UPLOAD_SIZE_BYTES:
            raise DocumentTooLargeError("The uploaded file exceeds the maximum allowed size.")
        return filename, suffix

    def ingest_upload(
        self,
        filename: str | None,
        content: bytes,
        user_id: str,
        content_type: str | None = None,
    ) -> dict:
        """Persist one unique upload, process it synchronously, and track status."""
        original_filename, extension = self._validate_upload(filename, content, content_type)
        document_id = str(uuid.uuid4())
        stored_filename = f"{document_id}{extension}"
        stored_path = self.upload_directory / stored_filename
        now = self._now()
        metadata = {
            "document_id": document_id,
            "user_id": str(user_id),
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_type": extension,
            "file_size": len(content),
            "content_hash": hashlib.sha256(content).hexdigest(),
            "status": "processing",
            "created_at": now,
            "updated_at": now,
            "chunk_count": 0,
        }

        try:
            self.metadata_collection.document(document_id).set(metadata)
            stored_path.write_bytes(content)
            chunk_count, extraction_info = self.process_document(
                file_path=stored_path,
                user_id=user_id,
                document_id=document_id,
                original_filename=original_filename,
            )
            metadata.update(
                {"status": "ready", "updated_at": self._now(), "chunk_count": chunk_count, **extraction_info}
            )
            self.metadata_collection.document(document_id).update(
                {
                    "status": metadata["status"],
                    "updated_at": metadata["updated_at"],
                    "chunk_count": chunk_count,
                    "processing_error": None,
                    **extraction_info,
                }
            )
            return self._display_metadata(document_id, metadata)
        except DocumentValidationError as error:
            self._mark_failed_and_cleanup(document_id, user_id, stored_path, error)
            raise
        except Exception as error:
            self._mark_failed_and_cleanup(document_id, user_id, stored_path, error)
            raise DocumentStorageError(self._safe_error(error)) from error

    def process_document(
        self,
        file_path: str | Path,
        user_id: str,
        document_id: str,
        original_filename: str,
    ) -> tuple[int, dict]:
        documents = self.loader.load_document(str(file_path))
        documents = [document for document in documents if document.page_content.strip()]
        if not documents:
            raise DocumentValidationError("No extractable text was found in this document.")

        chunks = self.splitter.split_documents(documents)
        chunks = [chunk for chunk in chunks if chunk.page_content.strip()]
        if not chunks:
            raise DocumentValidationError("No extractable text was found in this document.")

        for chunk_index, chunk in enumerate(chunks):
            chunk.metadata.update(
                {
                    "user_id": str(user_id),
                    "document_id": document_id,
                    "original_filename": original_filename,
                    "chunk_index": chunk_index,
                }
            )

        embeddings = self.embedding_manager.generate_embeddings(chunks)
        vector_ids = [f"{document_id}:{chunk_index}" for chunk_index in range(len(chunks))]
        self.vector_store.add_documents(chunks=chunks, embeddings=embeddings, ids=vector_ids)
        extraction_info = getattr(
            self.loader, "last_extraction_info", {"extraction_method": "native", "ocr_pages": 0}
        )
        return len(chunks), extraction_info

    def _mark_failed_and_cleanup(
        self,
        document_id: str,
        user_id: str,
        stored_path: Path,
        error: Exception,
    ) -> None:
        try:
            self.vector_store.delete_document_vectors(user_id, document_id)
        except Exception:
            pass
        try:
            stored_path.unlink(missing_ok=True)
        except OSError:
            pass
        try:
            self.metadata_collection.document(document_id).update(
                {
                    "status": "failed",
                    "updated_at": self._now(),
                    "processing_error": self._safe_error(error),
                    "chunk_count": 0,
                    "stored_filename": None,
                }
            )
        except Exception:
            pass

    def list_documents(self, user_id: str) -> list[dict]:
        try:
            snapshots = self.metadata_collection.where("user_id", "==", str(user_id)).stream()
            documents = [
                self._display_metadata(snapshot.id, snapshot.to_dict())
                for snapshot in snapshots
            ]
        except Exception as error:
            raise DocumentStorageError("Document service is temporarily unavailable.") from error
        return sorted(documents, key=lambda item: item["created_at"], reverse=True)

    def get_document(self, document_id: str, user_id: str) -> dict | None:
        try:
            snapshot = self.metadata_collection.document(document_id).get()
        except Exception as error:
            raise DocumentStorageError("Document service is temporarily unavailable.") from error
        if not snapshot.exists:
            return None
        data = snapshot.to_dict()
        if data.get("user_id") != str(user_id):
            return None
        return self._display_metadata(snapshot.id, data)

    def ready_document_ids(self, user_id: str, selected_ids: list[str]) -> list[str]:
        ready_ids = {
            document["document_id"]
            for document in self.list_documents(user_id)
            if document["status"] == "ready"
        }
        if not selected_ids:
            return sorted(ready_ids)
        requested_ids = {str(document_id) for document_id in selected_ids}
        if not requested_ids.issubset(ready_ids):
            raise DocumentValidationError("One or more selected documents are unavailable.")
        return sorted(requested_ids)

    def delete_document(self, document_id: str, user_id: str) -> None:
        try:
            snapshot = self.metadata_collection.document(document_id).get()
        except Exception as error:
            raise DocumentStorageError("Document service is temporarily unavailable.") from error
        if not snapshot.exists or snapshot.to_dict().get("user_id") != str(user_id):
            raise FileNotFoundError("Document not found.")

        data = snapshot.to_dict()
        stored_filename = data.get("stored_filename")
        stored_path = self.upload_directory / stored_filename if stored_filename else None
        if stored_path and stored_path.parent != self.upload_directory:
            raise DocumentStorageError("Invalid stored document reference.")

        try:
            self.vector_store.delete_document_vectors(user_id, document_id)
            if stored_path and stored_path.exists():
                stored_path.unlink()
            self.metadata_collection.document(document_id).delete()
        except Exception as error:
            raise DocumentStorageError("Document deletion could not be completed.") from error
