# AI-Powered RAG Chatbot

A FastAPI and React application for authenticated, document-grounded chat. Users register with email and password, complete required face registration, upload documents, and ask questions grounded in their own ready documents.

## Architecture

- `Frontend/`: Vite/React application for sessions, face capture, documents, conversations, and voice controls.
- `backend/`: FastAPI routes, services, JWT utilities, Firestore access, and RAG orchestration.
- `backend/Services/`: authentication, document lifecycle, conversation lifecycle, and web face records.
- `backend/rag/`: loading, splitting, embeddings, Chroma retrieval, prompts, and Groq chat engine.
- `member3/face/`: YuNet/SFace utilities. Three-angle scripts and `.npy` data are standalone/demo tooling; the web app uses Firestore embeddings.
- `member3/voice/`: existing local voice utilities used by web voice endpoints.

## Prerequisites

- Windows PowerShell, Python, Node.js/npm, and a Firebase project.
- YuNet and SFace ONNX models in `member3/face/models/`. Missing models may download on first face use.

## Configuration

Create a root `.env` file (never commit it):

```env
JWT_SECRET_KEY=use-a-long-random-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
GROQ_API_KEY=your-groq-key
MAX_UPLOAD_SIZE_MB=10
RAG_DISTANCE_THRESHOLD=1.6
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
# Use exactly one Firebase option:
FIREBASE_CREDENTIALS_JSON={...service-account-json...}
# GOOGLE_APPLICATION_CREDENTIALS=relative-or-absolute-path-to-service-account.json
```

The frontend optionally reads `VITE_API_URL`; it defaults to `http://127.0.0.1:8000` locally.

## OCR for scanned PDFs (Windows)

Digital PDFs use normal text extraction. If a PDF page has insufficient usable text, the backend automatically falls back to local English OCR and feeds the recognised text into the same document/RAG pipeline.

1. Install [Tesseract OCR for Windows](https://github.com/UB-Mannheim/tesseract/wiki).
2. Add `tesseract.exe` to your system `PATH`, or set `TESSERACT_CMD` in the root `.env` file. For example only: `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`.
3. Install project Python dependencies, including `pytesseract`, with `pip install -r requirements.txt`.

Tesseract is not required for backend startup or normal text-based documents. A scanned PDF requiring OCR fails safely if the engine is unavailable. OCR is English-only in the current version.

## Run locally

```powershell
cd "C:\Users\Mueed Ahmed\Desktop\AI-Powered-Rag-Chatbot"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

In another PowerShell window:

```powershell
cd "C:\Users\Mueed Ahmed\Desktop\AI-Powered-Rag-Chatbot\Frontend"
npm.cmd install
npm.cmd run dev
```

## Main workflow

1. Register an account. New users are sent to required face registration; there is no skip flow.
2. Sign in with password or the established face-login flow. Both create the same JWT-backed session.
3. Upload PDF, DOCX, TXT, or Markdown documents. Only ready documents may be used for RAG.
4. Select ready documents (or leave selection empty for all ready documents), then ask a question.
5. Conversations retain answers and source metadata. They can be reopened, renamed, and deleted.

## Tests and checks

```powershell
cd "C:\Users\Mueed Ahmed\Desktop\AI-Powered-Rag-Chatbot"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v

cd Frontend
npm.cmd run lint
npm.cmd run build
```

## Important limitations

- RAG answers are document-grounded only; no usable context produces a controlled response.
- Face login uses one web capture and Firestore embeddings. It has no liveness or anti-spoofing protection and is not high-security biometric authentication.
- `backend/chroma_db`, existing uploads, legacy Chroma vectors, and `member3/face/data` are preserved legacy/local data and are not automatically migrated or deleted.
- The historical filename `backend/rag/reteriver.py` remains for import stability.
