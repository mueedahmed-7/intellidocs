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
from database.firebase_db import messages_collection
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

        result = chat_engine.chat(
            question=request.question,
            top_k=request.top_k,
            user_id=current_user_id,
        )

        # Persist chat history to Firestore (non-fatal if it fails)
        try:
            messages_collection.add(
                {
                    "user_id": current_user_id,
                    "question": request.question,
                    "answer": result["answer"],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        except Exception as log_error:
            print(f"[CHAT HISTORY WARNING] Could not save message: {log_error}")

        return ChatResponse(
            answer=result["answer"]
        )

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


@router.get("/chat/history")
def get_chat_history(
    current_user_id: str = Depends(get_current_user_id),
):
    try:
        docs = (
            messages_collection
            .where("user_id", "==", current_user_id)
            .order_by("created_at")
            .stream()
        )

        history = [doc.to_dict() for doc in docs]

        return {"user_id": current_user_id, "history": history}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
