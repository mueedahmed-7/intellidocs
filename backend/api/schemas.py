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
        le=20,
        description="Number of chunks to retrieve",
    )

class ChatResponse(BaseModel):
    answer: str


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_stored: int

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

    @field_validator("password")
    @classmethod
    def password_must_fit_bcrypt(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError(
                "Password must be 72 bytes or fewer when UTF-8 encoded."
            )
        return password


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
