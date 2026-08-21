# import shutil
# from pathlib import Path
# from fastapi import (
#     APIRouter,
#     UploadFile,
#     File,
#     HTTPException,
# )
# from api.schemas import (
#     ChatRequest,
#     ChatResponse,
#     UploadResponse,
#     RegisterRequest,
#     LoginRequest,
#     LoginResponse,
# )

# from Services.auth_service import AuthService
# from services import chat_engine
# from Services.document_service import DocumentService
# from utils.jwt_handler import create_access_token



# router = APIRouter()
# document_service = DocumentService()
# UPLOAD_DIR = Path("uploads")
# UPLOAD_DIR.mkdir(exist_ok=True)

# ALLOWED_EXTENSIONS = {
#     ".pdf",
#     ".docx",
#     ".txt",
#     ".md",
# }

# @router.post("/auth/register")
# def register(
#     request: RegisterRequest,
# ):

#     try:

#         user = AuthService.register_user(
#             name=request.name,
#             email=request.email,
#             password=request.password,
#         )

#         return {
#             "message": "User registered successfully.",
#             "user": user,
#         }

#     except ValueError as e:

#         raise HTTPException(
#             status_code=400,
#             detail=str(e),
#         )

# @router.post(
#     "/chat",
#     response_model=ChatResponse,
# )
# def chat(request: ChatRequest):

#     try:

#         result = chat_engine.chat(
#             question=request.question,
#             top_k=request.top_k,
#         )

#         return ChatResponse(
#             answer=result["answer"]
#         )

#     except Exception as e:

#         raise HTTPException(
#             status_code=500,
#             detail=str(e),
#         )


# @router.post(
#     "/documents/upload",
#     response_model=UploadResponse,
# )
# def upload_document(
#     file: UploadFile = File(...),
# ):

#     allowed_extensions = {
#         ".pdf",
#         ".docx",
#         ".txt",
#         ".md",
#     }

#     extension = Path(file.filename).suffix.lower()

#     if extension not in allowed_extensions:
#         raise HTTPException(
#             status_code=400,
#             detail="Unsupported file type.",
#         )

#     try:
#         # Save uploaded file
#         save_path = UPLOAD_DIR / file.filename

#         with save_path.open("wb") as buffer:
#             shutil.copyfileobj(
#                 file.file,
#                 buffer,
#             )

#         # Process through RAG ingestion
#         result = document_service.process_document(
#             file_path=str(save_path),
#             user_id="test-user",
#         )

#         return UploadResponse(
#             message="Document uploaded and processed successfully.",
#             filename=file.filename,
#             chunks_stored=result["chunks"],
#         )

#     except Exception as e:

#         raise HTTPException(
#             status_code=500,
#             detail=str(e),
#         )

#     finally:
#         file.file.close()

# @router.post(
#     "/auth/login",
#     response_model=LoginResponse,
# )
# def login(
#     request: LoginRequest,
# ):

#     try:

#         user = AuthService.login_user(
#             email=request.email,
#             password=request.password,
#         )

#         token = create_access_token(
#             user_id=user["id"],
#         )

#         return LoginResponse(
#             access_token=token,
#             token_type="bearer",
#         )

#     except ValueError as e:

#         raise HTTPException(
#             status_code=401,
#             detail=str(e),
#         )
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from api.schemas import (
    ChatRequest,
    ChatResponse,
    UploadResponse,
    RegisterRequest,
    LoginRequest,
    LoginResponse,
)

from Services.auth_service import AuthService
from services import chat_engine
from Services.document_service import DocumentService
from utils.jwt_handler import create_access_token
from utils.auth_dependency import get_current_user_id
from database.firebase_db import chats_collection, messages_collection
from datetime import datetime, timezone



router = APIRouter()
document_service = DocumentService()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}

@router.post("/auth/register")
def register(
    request: RegisterRequest,
):

    try:

        user = AuthService.register_user(
            name=request.name,
            email=request.email,
            password=request.password,
        )

        return {
            "message": "User registered successfully.",
            "user": user,
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
):

    try:

        now = datetime.now(timezone.utc).isoformat()
        chat_id = request.chat_id

        if chat_id:
            chat_snapshot = chats_collection.document(chat_id).get()
            if (
                not chat_snapshot.exists
                or chat_snapshot.to_dict().get("user_id") != current_user_id
            ):
                raise HTTPException(status_code=404, detail="Conversation not found.")
        else:
            # The first question becomes the readable title shown in the
            # conversation sidebar.
            chat_title = " ".join(request.question.split())[:60]
            chat_reference = chats_collection.document()
            chat_id = chat_reference.id
            chat_reference.set(
                {
                    "user_id": current_user_id,
                    "title": chat_title or "New conversation",
                    "created_at": now,
                    "updated_at": now,
                }
            )

        result = chat_engine.chat(
            question=request.question,
            top_k=request.top_k,
            user_id=current_user_id,
        )

        # Store every turn under its conversation so the user can reopen it.
        try:
            messages_collection.add(
                {
                    "user_id": current_user_id,
                    "chat_id": chat_id,
                    "question": request.question,
                    "answer": result["answer"],
                    "created_at": now,
                }
            )
            chats_collection.document(chat_id).update({"updated_at": now})
        except Exception as log_error:
            print(f"[CHAT HISTORY WARNING] Could not save message: {log_error}")

        return ChatResponse(
            answer=result["answer"],
            chat_id=chat_id,
        )

    except HTTPException:
        raise
    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post(
    "/documents/upload",
    response_model=UploadResponse,
)
def upload_document(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id),
):

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
    }

    extension = Path(file.filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type.",
        )

    try:
        # Save uploaded file
        safe_filename = Path(file.filename).name
        save_path = UPLOAD_DIR / f"{current_user_id}_{safe_filename}"

        with save_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        # Process through RAG ingestion
        result = document_service.process_document(
            file_path=str(save_path),
            user_id=current_user_id,
            filename=safe_filename,
        )

        return UploadResponse(
            message="Document uploaded and processed successfully.",
            filename=safe_filename,
            chunks_stored=result["chunks"],
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        file.file.close()

@router.post(
    "/auth/login",
    response_model=LoginResponse,
)
def login(
    request: LoginRequest,
):

    try:

        user = AuthService.login_user(
            email=request.email,
            password=request.password,
        )

        token = create_access_token(
            user_id=user["id"],
        )

        return LoginResponse(
            access_token=token,
            token_type="bearer",
        )

    except ValueError as e:

        raise HTTPException(
            status_code=401,
            detail=str(e),
        )


@router.get("/chats")
def get_chats(
    current_user_id: str = Depends(get_current_user_id),
):
    try:
        docs = chats_collection.where("user_id", "==", current_user_id).stream()
        chats = [
            {"id": doc.id, **doc.to_dict()}
            for doc in docs
        ]
        # Messages created before conversations were introduced remain
        # available as one read-only legacy conversation.
        legacy_messages = [
            doc.to_dict()
            for doc in messages_collection.where("user_id", "==", current_user_id).stream()
            if not doc.to_dict().get("chat_id")
        ]
        if legacy_messages:
            chats.append(
                {
                    "id": "legacy-history",
                    "title": "Earlier chat history",
                    "updated_at": max(
                        message.get("created_at", "") for message in legacy_messages
                    ),
                }
            )
        chats.sort(key=lambda chat: chat.get("updated_at", ""), reverse=True)

        return {"chats": chats}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/chats/{chat_id}/messages")
def get_chat_messages(
    chat_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    try:
        if chat_id == "legacy-history":
            docs = messages_collection.where("user_id", "==", current_user_id).stream()
            messages = [
                {"id": doc.id, **doc.to_dict()}
                for doc in docs
                if not doc.to_dict().get("chat_id")
            ]
            messages.sort(key=lambda message: message.get("created_at", ""))
            return {
                "chat": {"id": "legacy-history", "title": "Earlier chat history"},
                "messages": messages,
            }

        chat_snapshot = chats_collection.document(chat_id).get()
        if (
            not chat_snapshot.exists
            or chat_snapshot.to_dict().get("user_id") != current_user_id
        ):
            raise HTTPException(status_code=404, detail="Conversation not found.")

        # Ownership was checked against the parent chat above, so querying by
        # chat_id alone avoids requiring a Firestore composite index.
        docs = messages_collection.where("chat_id", "==", chat_id).stream()
        messages = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        messages.sort(key=lambda message: message.get("created_at", ""))

        return {"chat": {"id": chat_snapshot.id, **chat_snapshot.to_dict()}, "messages": messages}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
