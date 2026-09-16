from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.config import allowed_origins
from backend.Services.face_service import FaceService, FaceStorageError, FaceValidationError
from backend.utils.auth_dependency import get_current_user_id
from backend.utils.jwt_handler import create_access_token
from member3.voice.tts.text_to_speech import speak_text, stop_speaking
from member3.voice.stt.speech_to_text import transcribe_audio_file


app = FastAPI(
    title="AI RAG Chatbot API",
    description="Backend API for an AI-powered RAG chatbot.",
    version="1.0.0",
)

ALLOWED_ORIGINS = allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "AI RAG Chatbot Backend Running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/face/register")
async def register_face(
    image: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id),
):
    try:
        image_bytes = await image.read()
        result = FaceService.register_face(
            user_id=current_user_id,
            image_bytes=image_bytes,
        )
        return {
            "success": True,
            "message": "Face registered successfully.",
            "user_id": result["user_id"],
        }
    except FaceValidationError as error:
        raise HTTPException(status_code=422, detail=str(error))
    except FaceStorageError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except Exception:
        raise HTTPException(status_code=500, detail="Face registration failed.")


@app.post("/face/login")
async def face_login(image: UploadFile = File(...)):
    try:
        image_bytes = await image.read()
        result = FaceService.login_with_face(image_bytes=image_bytes)

        if not result.get("success"):
            raise HTTPException(status_code=401, detail=result.get("message", "Face not recognized."))

        token = create_access_token(user_id=result["user_id"])
        return {
            "success": True,
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": result["user_id"], "name": result["name"], "email": result["email"]},
        }
    except FaceValidationError as error:
        raise HTTPException(status_code=422, detail=str(error))
    except FaceStorageError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except Exception:
        raise HTTPException(status_code=500, detail="Face login failed.")


@app.post("/voice/speak")
def voice_speak(text: str = Form(...)):
    try:
        if not text.strip():
            return {"success": False, "message": "No text provided."}

        speak_text(text)
        return {"success": True, "message": "Speech completed."}
    except Exception:
        raise HTTPException(status_code=503, detail="Text-to-speech is unavailable.")


@app.post("/voice/stop")
def voice_stop():
    stopped = stop_speaking()
    return {
        "success": True,
        "message": "Speech stopped." if stopped else "No speech was active.",
    }


@app.post("/voice/transcribe")
async def voice_transcribe(audio: UploadFile = File(...), language: str | None = Form(None)):
    """Transcribe a browser recording with the locally installed Whisper model."""
    try:
        audio_bytes = await audio.read()
        text = transcribe_audio_file(audio_bytes, audio.filename or "recording.webm", language)
        if not text:
            return {"success": False, "message": "No speech was detected.", "text": ""}
        return {"success": True, "text": text}
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        print(f"[STT ERROR] {error}")
        raise HTTPException(
            status_code=503,
            detail="Local speech-to-text is unavailable. Ensure Whisper and FFmpeg are installed.",
        ) from error
