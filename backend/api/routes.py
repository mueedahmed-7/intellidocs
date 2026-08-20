import shutil
from pathlib import Path
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)
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
def chat(request: ChatRequest):

    try:

        result = chat_engine.chat(
            question=request.question,
            top_k=request.top_k,
        )

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
        save_path = UPLOAD_DIR / file.filename

        with save_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        # Process through RAG ingestion
        result = document_service.process_document(
            file_path=str(save_path),
            user_id="test-user",
        )

        return UploadResponse(
            message="Document uploaded and processed successfully.",
            filename=file.filename,
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