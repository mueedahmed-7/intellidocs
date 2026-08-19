from fastapi import APIRouter

from api.schemas import ChatRequest, ChatResponse


router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    return {
        "answer": "Test response"
    }