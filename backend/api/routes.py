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
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from backend.api.schemas import (
    ChatRequest,
    ChatResponse,
    UploadResponse,
    DocumentListResponse,
    DocumentResponse,
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    UserProfile,
    ChatListResponse,
    ChatMessagesResponse,
    RenameChatRequest,
    RenameChatResponse,
    DeleteChatResponse,
)

from backend.Services.auth_service import (
    AuthService,
    AuthStorageError,
    DuplicateEmailError,
    InvalidCredentialsError,
)
from backend.services import get_chat_engine
from backend.rag.chatengine import ChatEngine
from backend.Services.document_service import (
    DocumentService,
    DocumentStorageError,
    DocumentTooLargeError,
    DocumentValidationError,
)
from backend.utils.jwt_handler import create_access_token
from backend.utils.auth_dependency import get_current_user_id
from backend.Services.conversation_service import (
    ConversationNotFoundError,
    ConversationService,
    ConversationStorageError,
)



router = APIRouter()
document_service = DocumentService()
conversation_service = ConversationService()

@router.post("/auth/register", response_model=AuthResponse)
def register(
    request: RegisterRequest,
):

    try:

        user = AuthService.register_user(
            name=request.name,
            email=request.email,
            password=request.password,
        )

        return AuthResponse(
            access_token=create_access_token(user_id=user["id"]),
            token_type="bearer",
            user=UserProfile(**user),
        )

    except DuplicateEmailError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except AuthStorageError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
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

        chat_id = request.chat_id

        if chat_id:
            conversation_service._owned_chat(chat_id, current_user_id)

        eligible_document_ids = document_service.ready_document_ids(
            current_user_id, request.document_ids
        )

        # A new chat is intentionally lazy: no permanent empty record exists
        # until the first question can actually be processed.
        if not chat_id:
            chat_id = conversation_service.create_chat(current_user_id, request.question)

        history_messages = conversation_service.recent_history(chat_id, current_user_id, limit=6)
        conversation_history = "\n".join(
            f"{'User' if item['role'] == 'user' else 'Assistant'}: {item['content']}"
            for item in history_messages
        )
        # Selection limits RAG scope. It does not make every later question a
        # document question: routing is deliberately decided per user message.
        document_mode = ChatEngine.should_use_document_mode(
            request.question,
            has_selected_documents=bool(eligible_document_ids),
            history_messages=history_messages,
        )

        if document_mode and not eligible_document_ids:
            result = {"answer": "I couldn't find that information in the selected documents.", "sources": []}
        else:
            result = get_chat_engine().chat(
                question=request.question,
                top_k=request.top_k,
                user_id=current_user_id,
                document_ids=eligible_document_ids,
                conversation_history=conversation_history,
                document_mode=document_mode,
            )

        conversation_service.save_exchange(chat_id, current_user_id, request.question, result["answer"], result["sources"])

        return ChatResponse(
            answer=result["answer"],
            chat_id=chat_id,
            sources=result["sources"],
        )

    except DocumentValidationError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    except ConversationStorageError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except HTTPException:
        raise
    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Chat could not be completed. Please try again.",
        )


@router.post(
    "/documents/upload",
    response_model=UploadResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id),
):

    try:
        result = document_service.ingest_upload(
            filename=file.filename,
            content=await file.read(),
            user_id=current_user_id,
            content_type=file.content_type,
        )

        return UploadResponse(
            message="Document uploaded and processed successfully.",
            filename=result["original_filename"],
            chunks_stored=result["chunk_count"],
            document_id=result["document_id"],
            status=result["status"],
        )
    except DocumentTooLargeError as error:
        raise HTTPException(status_code=413, detail=str(error))
    except DocumentValidationError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except DocumentStorageError as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/documents", response_model=DocumentListResponse)
def list_documents(current_user_id: str = Depends(get_current_user_id)):
    try:
        return DocumentListResponse(documents=document_service.list_documents(current_user_id))
    except DocumentStorageError as error:
        raise HTTPException(status_code=503, detail=str(error))


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, current_user_id: str = Depends(get_current_user_id)):
    try:
        document = document_service.get_document(document_id, current_user_id)
    except DocumentStorageError as error:
        raise HTTPException(status_code=503, detail=str(error))
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentResponse(**document)


@router.delete("/documents/{document_id}")
def delete_document(document_id: str, current_user_id: str = Depends(get_current_user_id)):
    try:
        document_service.delete_document(document_id, current_user_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found.")
    except DocumentStorageError as error:
        raise HTTPException(status_code=500, detail=str(error))
    return {"message": "Document deleted successfully.", "document_id": document_id}

@router.post(
    "/auth/login",
    response_model=AuthResponse,
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

        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user=UserProfile(**user),
        )

    except InvalidCredentialsError as error:

        raise HTTPException(
            status_code=401,
            detail=str(error),
        )
    except AuthStorageError as error:
        raise HTTPException(status_code=503, detail=str(error))


@router.get("/auth/me", response_model=UserProfile)
def get_current_user(
    current_user_id: str = Depends(get_current_user_id),
):
    try:
        user = AuthService.get_user_by_id(current_user_id)
    except AuthStorageError as error:
        raise HTTPException(status_code=503, detail=str(error))

    if user is None:
        raise HTTPException(status_code=401, detail="Session is no longer valid. Please log in again.")

    return UserProfile(**user)


@router.get("/chats", response_model=ChatListResponse)
def get_chats(
    current_user_id: str = Depends(get_current_user_id),
):
    try:
        return ChatListResponse(chats=conversation_service.list_chats(current_user_id))
    except ConversationStorageError as error:
        raise HTTPException(status_code=503, detail=str(error))


@router.get("/chats/{chat_id}/messages", response_model=ChatMessagesResponse)
def get_chat_messages(
    chat_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    try:
        chat, messages = conversation_service.get_messages(chat_id, current_user_id)
        return ChatMessagesResponse(chat=chat, messages=messages)
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    except ConversationStorageError as error:
        raise HTTPException(status_code=503, detail=str(error))


@router.patch("/chats/{chat_id}", response_model=RenameChatResponse)
def rename_chat(chat_id: str, request: RenameChatRequest, current_user_id: str = Depends(get_current_user_id)):
    try:
        return RenameChatResponse(**conversation_service.rename_chat(chat_id, current_user_id, request.title))
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    except ConversationStorageError as error:
        raise HTTPException(status_code=503, detail=str(error))


@router.delete("/chats/{chat_id}", response_model=DeleteChatResponse)
def delete_chat(chat_id: str, current_user_id: str = Depends(get_current_user_id)):
    try:
        result = conversation_service.delete_chat(chat_id, current_user_id)
        return DeleteChatResponse(message="Conversation deleted successfully.", chat_id=result["chat_id"])
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    except ConversationStorageError as error:
        raise HTTPException(status_code=503, detail=str(error))
