# from pydantic import BaseModel, Field


# class ChatRequest(BaseModel):
#     question: str = Field(
#         ...,
#         min_length=1,
#         description="User's question",
#     )

#     top_k: int = Field(
#         default=5,
#         ge=1,
#         le=20,
#         description="Number of chunks to retrieve",
#     )


# class ChatResponse(BaseModel):
#     answer: str


# class UploadResponse(BaseModel):
#     message: str
#     filename: str
#     chunks_stored: int

# class RegisterRequest(BaseModel):
#     name: str = Field(
#         ...,
#         min_length=2,
#         max_length=100,
#     )

#     email: str = Field(
#         ...,
#         min_length=5,
#         max_length=255,
#     )

#     password: str = Field(
#         ...,
#         min_length=8,
#         max_length=128,
#     )


# class LoginRequest(BaseModel):
#     email: str
#     password: str


# class LoginResponse(BaseModel):
#     access_token: str
#     token_type: str
import re

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="User's question",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of chunks to retrieve",
    )

    chat_id: str | None = Field(
        default=None,
        description="Existing conversation ID. Omit to start a new conversation.",
    )
    document_ids: list[str] = Field(default_factory=list)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, question: str) -> str:
        normalized = question.strip()
        if not normalized:
            raise ValueError("Question must not be blank.")
        if len(normalized) > 5000:
            raise ValueError("Question must be 5000 characters or fewer.")
        return normalized

class SourceReference(BaseModel):
    document_id: str
    filename: str
    chunk_index: int
    page: int | None = None
    distance: float

class ChatResponse(BaseModel):
    answer: str
    chat_id: str
    sources: list[SourceReference] = Field(default_factory=list)


class ChatSummary(BaseModel):
    chat_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int


class ChatListResponse(BaseModel):
    chats: list[ChatSummary]


class ChatMessage(BaseModel):
    message_id: str
    role: str
    content: str
    created_at: str
    sources: list[SourceReference] = Field(default_factory=list)


class ChatMessagesResponse(BaseModel):
    chat: ChatSummary
    messages: list[ChatMessage]


class RenameChatRequest(BaseModel):
    title: str = Field(..., max_length=100)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, title: str) -> str:
        normalized = " ".join(title.split())
        if not normalized:
            raise ValueError("Conversation title must not be blank.")
        return normalized


class RenameChatResponse(BaseModel):
    chat_id: str
    title: str
    updated_at: str


class DeleteChatResponse(BaseModel):
    message: str
    chat_id: str


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_stored: int
    document_id: str
    status: str


class DocumentResponse(BaseModel):
    document_id: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    created_at: str
    updated_at: str
    chunk_count: int = 0
    processing_error: str | None = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]

class RegisterRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, name: str) -> str:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Name must not be blank.")
        return normalized_name

    @field_validator("email")
    @classmethod
    def normalize_and_validate_email(cls, email: str) -> str:
        normalized_email = email.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized_email):
            raise ValueError("A valid email address is required.")
        return normalized_email

    @field_validator("password")
    @classmethod
    def password_must_fit_bcrypt(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError(
                "Password must be 72 bytes or fewer when UTF-8 encoded."
            )
        return password


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_and_validate_email(cls, email: str) -> str:
        return RegisterRequest.normalize_and_validate_email(email)

class UserProfile(BaseModel):
    id: str
    name: str
    email: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile
