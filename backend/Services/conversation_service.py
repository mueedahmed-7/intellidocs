"""PostgreSQL-backed conversation lifecycle helpers.

New messages are role-based.  The reader deliberately also understands the
legacy combined question/answer records so existing history stays visible.
"""

from datetime import datetime, timezone

from backend.database.postgres_db import chats_collection, messages_collection

# Retained as a harmless compatibility seam for existing isolated tests.  The
# SQLAlchemy implementation performs deletion through repository references.
db = None


class ConversationStorageError(Exception):
    """Raised when chat data cannot be read or written safely."""


class ConversationNotFoundError(Exception):
    """Raised for missing chats and chats owned by another user."""


def _now():
    return datetime.now(timezone.utc).isoformat()


def _sort_value(value):
    return value.isoformat() if hasattr(value, "isoformat") else str(value or "")


def _title_from_question(question):
    normalized = " ".join(question.split())
    return normalized[:60] or "New Conversation"


class ConversationService:
    def _owned_chat(self, chat_id, user_id):
        try:
            snapshot = chats_collection.document(chat_id).get()
        except Exception as error:
            raise ConversationStorageError("Conversation storage is unavailable.") from error
        if not snapshot.exists or snapshot.to_dict().get("user_id") != user_id:
            raise ConversationNotFoundError()
        return snapshot

    def create_chat(self, user_id, first_question):
        now = _now()
        try:
            reference = chats_collection.document()
            reference.set({
                "user_id": user_id,
                "title": _title_from_question(first_question),
                "created_at": now,
                "updated_at": now,
                "message_count": 0,
            })
            return reference.id
        except Exception as error:
            raise ConversationStorageError("Conversation storage is unavailable.") from error

    def list_chats(self, user_id):
        try:
            chats = []
            for snapshot in chats_collection.where("user_id", "==", user_id).stream():
                data = snapshot.to_dict() or {}
                chats.append({
                    "chat_id": snapshot.id,
                    "title": data.get("title") or "New Conversation",
                    "created_at": _sort_value(data.get("created_at")),
                    "updated_at": _sort_value(data.get("updated_at")),
                    "message_count": int(data.get("message_count") or 0),
                })

            legacy = [
                snapshot.to_dict() or {}
                for snapshot in messages_collection.where("user_id", "==", user_id).stream()
                if not (snapshot.to_dict() or {}).get("chat_id")
            ]
            if legacy:
                chats.append({
                    "chat_id": "legacy-history",
                    "title": "Earlier chat history",
                    "created_at": "",
                    "updated_at": max((_sort_value(item.get("created_at")) for item in legacy), default=""),
                    "message_count": len(legacy) * 2,
                })
            return sorted(chats, key=lambda item: item["updated_at"], reverse=True)
        except Exception as error:
            raise ConversationStorageError("Conversation storage is unavailable.") from error

    def get_messages(self, chat_id, user_id):
        if chat_id == "legacy-history":
            try:
                records = [
                    (snapshot.id, snapshot.to_dict() or {})
                    for snapshot in messages_collection.where("user_id", "==", user_id).stream()
                    if not (snapshot.to_dict() or {}).get("chat_id")
                ]
            except Exception as error:
                raise ConversationStorageError("Conversation storage is unavailable.") from error
            chat = {"chat_id": chat_id, "title": "Earlier chat history", "created_at": "", "updated_at": "", "message_count": len(records) * 2}
        else:
            snapshot = self._owned_chat(chat_id, user_id)
            data = snapshot.to_dict() or {}
            chat = {
                "chat_id": snapshot.id, "title": data.get("title") or "New Conversation",
                "created_at": _sort_value(data.get("created_at")), "updated_at": _sort_value(data.get("updated_at")),
                "message_count": int(data.get("message_count") or 0),
            }
            try:
                records = [(item.id, item.to_dict() or {}) for item in messages_collection.where("chat_id", "==", chat_id).stream()]
            except Exception as error:
                raise ConversationStorageError("Conversation storage is unavailable.") from error

        messages = []
        for message_id, data in records:
            timestamp = _sort_value(data.get("created_at"))
            if data.get("role") in {"user", "assistant"} and isinstance(data.get("content"), str):
                messages.append({"message_id": message_id, "role": data["role"], "content": data["content"], "created_at": timestamp, "sources": data.get("sources") or [], "_order": data.get("message_order", 0)})
            elif data.get("question") is not None or data.get("answer") is not None:
                # Compatibility for Phase 5 combined exchange records.
                if data.get("question"):
                    messages.append({"message_id": f"{message_id}-user", "role": "user", "content": str(data["question"]), "created_at": timestamp, "sources": [], "_order": 0})
                if data.get("answer"):
                    messages.append({"message_id": f"{message_id}-assistant", "role": "assistant", "content": str(data["answer"]), "created_at": timestamp, "sources": data.get("sources") or [], "_order": 1})
        ordered = sorted(messages, key=lambda item: (item["created_at"], item["_order"], item["message_id"]))
        for item in ordered:
            item.pop("_order", None)
        return chat, ordered

    def recent_history(self, chat_id, user_id, limit=6):
        _, messages = self.get_messages(chat_id, user_id)
        return messages[-limit:]

    def save_exchange(self, chat_id, user_id, question, answer, sources):
        # Verify ownership again at the write boundary and write no partial
        # history if the provider failed before this method was reached.
        self._owned_chat(chat_id, user_id)
        now = _now()
        try:
            messages_collection.add({"user_id": user_id, "chat_id": chat_id, "role": "user", "content": question, "created_at": now, "message_order": 0, "sources": []})
            messages_collection.add({"user_id": user_id, "chat_id": chat_id, "role": "assistant", "content": answer, "created_at": now, "message_order": 1, "sources": sources or []})
            chats_collection.document(chat_id).update({"updated_at": now, "message_count": self._message_count(chat_id)})
        except Exception as error:
            raise ConversationStorageError("Conversation could not be saved.") from error

    def _message_count(self, chat_id):
        return sum(1 for _ in messages_collection.where("chat_id", "==", chat_id).stream())

    def rename_chat(self, chat_id, user_id, title):
        snapshot = self._owned_chat(chat_id, user_id)
        now = _now()
        try:
            chats_collection.document(snapshot.id).update({"title": title, "updated_at": now})
        except Exception as error:
            raise ConversationStorageError("Conversation could not be renamed.") from error
        return {"chat_id": snapshot.id, "title": title, "updated_at": now}

    def delete_chat(self, chat_id, user_id):
        if chat_id == "legacy-history":
            raise ConversationNotFoundError()
        snapshot = self._owned_chat(chat_id, user_id)
        try:
            # Ownership is established through the parent before this query.
            # Each message also carries user_id, so cleanup cannot cross users.
            records = [item for item in messages_collection.where("chat_id", "==", chat_id).stream() if (item.to_dict() or {}).get("user_id") == user_id]
            for record in records:
                reference = getattr(record, "reference", messages_collection.document(record.id))
                reference.delete()
            chats_collection.document(snapshot.id).delete()
            return {"chat_id": chat_id, "deleted_messages": len(records)}
        except Exception as error:
            raise ConversationStorageError("Conversation could not be deleted safely.") from error
