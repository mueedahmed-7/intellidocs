from fastapi import FastAPI

from api.routes import router


app = FastAPI(
    title="AI RAG Chatbot API",
    description="Backend API for an AI-powered RAG chatbot.",
    version="1.0.0",
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "AI RAG Chatbot Backend Running"
    }