# IntelliDocs

**A full-stack RAG application for asking evidence-grounded questions about your own documents.**

## Overview

Finding information across PDFs, Word files, and notes is slow, and a general chatbot cannot reliably use a user's private files as evidence. IntelliDocs turns supported uploads into a searchable conversational workspace.

I built the React/FastAPI application and its RAG pipeline: document extraction and OCR fallback, chunking, embedding, persistent vector search, evidence-only prompting, chat persistence, and authenticated ownership boundaries. It also includes optional face login and voice capabilities.

## At a Glance

| Question | Verified answer |
| --- | --- |
| **What it solves** | Makes user-owned documents searchable through a chat interface instead of relying on general-model knowledge alone. |
| **What I built** | React/Vite client, FastAPI API, PostgreSQL-backed application data, persistent Chroma retrieval, and a complete upload-to-answer workflow. |
| **AI/ML demonstrated** | RAG, recursive chunking, normalized Sentence Transformer embeddings, vector similarity search, retrieval filtering, prompt grounding, OCR, and face embeddings. |
| **Evidence it works** | The audited checkout passed **58 backend tests**, plus frontend linting and a production build. |
| **How to run it** | Follow [Getting Started](#getting-started); Windows startup scripts launch the API on `:8000` and client on `:5173`. |

## Core Capabilities

- Upload and index **PDF, DOCX, TXT, and Markdown** files.
- Extract native PDF text with a page-level **Tesseract OCR fallback**; split it into 1,000-character chunks with 200-character overlap.
- Create normalized **`all-MiniLM-L6-v2`** embeddings, persist them in **Chroma**, and retrieve only chunks belonging to the current user and selected documents.
- Keep document answers evidence-bound; return a controlled no-evidence response rather than substituting a general answer.
- Support separate general AI chat, persisted conversations, Markdown rendering, JWT/bcrypt authentication, and ownership-aware document cleanup.
- Offer browser camera capture with **YuNet + SFace** face matching, browser Web Speech API input, pyttsx3 answer playback, and a Whisper transcription endpoint.

## Demo

Watch the recorded walkthrough: [IntelliDocs v1.0.0 — Demo Release](https://github.com/mueedahmed-7/intellidocs/releases/tag/V1.0.0).

## How It Works

### Document ingestion and grounded answers

```text
Upload
  -> validate type, MIME type, and size
  -> save file + document metadata
  -> extract text (native PDF text, or OCR when needed)
  -> split into overlapping chunks
  -> create normalized embeddings
  -> persist chunks and metadata in Chroma

Question about selected documents
  -> embed query
  -> retrieve matching chunks for the current user + selected documents
  -> apply distance threshold and deduplication
  -> build evidence-only prompt with recent conversation context
  -> Groq LLM generates answer
  -> return answer + source metadata and save the exchange
```

Document selection scopes retrieval, while message-level routing decides whether to use RAG or general chat. If document mode has no relevant evidence, the application returns a controlled "couldn't find" response instead of falling back to a general answer.

## Architecture

```mermaid
flowchart LR
    Browser[React + Vite browser client]
    API[FastAPI API]
    DB[(PostgreSQL)]
    Files[Persistent upload storage]
    Extract[PDF / DOCX / TXT / MD extraction]
    OCR[Tesseract OCR\nfor low-text PDF pages]
    Split[Recursive text splitter]
    Embed[Sentence Transformers\nall-MiniLM-L6-v2]
    Chroma[(Persistent Chroma)]
    Retrieve[User- and document-scoped retrieval]
    LLM[Groq ChatGroq\nopenai/gpt-oss-120b]
    Face[OpenCV YuNet + SFace]
    Voice[Browser Web Speech API\n+ pyttsx3 / Whisper endpoints]

    Browser <-->|JWT-authenticated HTTP| API
    Browser -->|camera frame| API
    Browser --> Voice
    API --> DB
    API --> Face
    API --> Voice
    API --> Files
    Files --> Extract
    Extract -->|scanned or low-text page| OCR
    Extract --> Split --> Embed --> Chroma
    API --> Retrieve --> Chroma
    Retrieve --> LLM
    LLM --> API
```

## Tech Stack

| Area | Technologies verified in this repository |
| --- | --- |
| AI / RAG | LangChain, Sentence Transformers (`all-MiniLM-L6-v2`), Chroma, Groq via `langchain-groq` (`openai/gpt-oss-120b`) |
| Backend | Python, FastAPI, Uvicorn, Pydantic, SQLAlchemy, psycopg |
| Frontend | React, Vite, React Router, React Markdown, remark-gfm |
| Database & storage | PostgreSQL, local/persistent filesystem uploads, persistent Chroma storage |
| Document processing | PyMuPDF, docx2txt, pytesseract / Tesseract |
| Computer vision | OpenCV, YuNet, SFace, NumPy |
| Voice | Browser Web Speech API, pyttsx3, OpenAI Whisper |
| Security & testing | bcrypt, python-jose JWT, Python `unittest`, ESLint |

## Project Structure

```text
backend/
  api/                 # FastAPI routes and request/response schemas
  Services/            # Authentication, documents, conversations, OCR, face service
  rag/                 # Loading, splitting, embeddings, Chroma, retrieval, prompts, chat
  database/            # SQLAlchemy models and PostgreSQL repository adapters
  main.py              # FastAPI app, CORS, face and voice endpoints
Frontend/
  src/pages/           # Login, registration, face, and chat screens
  src/api.js           # API client and session storage
member3/
  face/                # YuNet/SFace utilities and bundled ONNX models
  voice/               # Whisper transcription and pyttsx3 speech modules
tests/                 # Unit and smoke tests
scripts/               # Windows PowerShell startup scripts
.env.example           # Safe backend configuration template
```

## Getting Started

### Prerequisites

- Python **3.10+** (the repository's local environment uses Python 3.13).
- Node.js and npm.
- PostgreSQL.
- A Groq API key for chat generation.
- Tesseract OCR for scanned PDF support (optional for digital PDFs).
- On Windows, an installed SAPI voice for the server-side text-to-speech feature. Whisper transcription also requires FFmpeg when using browser-recorded formats.

### 1. Clone and create a virtual environment

```powershell
git clone https://github.com/mueedahmed-7/intellidocs.git
cd AI-Powered-Rag-Chatbot

py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On macOS/Linux, activate the environment with `source .venv/bin/activate` instead.

### 2. Configure PostgreSQL and environment variables

Create a PostgreSQL database named `intellidocs`, then copy the safe templates:

```powershell
Copy-Item .env.example .env
Copy-Item Frontend\.env.example Frontend\.env
```

Use placeholders only—never commit `.env` files or real API keys. A minimal backend `.env` looks like this:

```dotenv
DATABASE_URL=postgresql+psycopg://POSTGRES_USER:POSTGRES_PASSWORD@localhost:5432/intellidocs
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
GROQ_API_KEY=replace-with-your-groq-api-key
PERSISTENT_DATA_DIR=data
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
MAX_UPLOAD_SIZE_MB=10
RAG_DISTANCE_THRESHOLD=1.6

# Optional: needed only for scanned PDFs when Tesseract is not on PATH.
# TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
```

Set the frontend endpoint in `Frontend/.env`:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 3. Initialize the database and install the frontend

```powershell
.\.venv\Scripts\python.exe -m backend.scripts.init_db

Set-Location Frontend
npm.cmd install
Set-Location ..
```

### 4. Start the application

Use the provided Windows PowerShell scripts in two terminals:

```powershell
# Terminal 1
.\scripts\start-backend.ps1
```

```powershell
# Terminal 2
.\scripts\start-frontend.ps1
```

Open `http://localhost:5173`. The backend health check is available at `http://127.0.0.1:8000/health`.

For manual startup, run `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000` from the project root and `npm run dev -- --host localhost --port 5173 --strictPort` from `Frontend/`.

### Deployment configuration

The repository includes Render service configuration files for the backend and frontend. They are configuration templates, not evidence of a live deployment. Configure `DATABASE_URL`, `JWT_SECRET_KEY`, `GROQ_API_KEY`, and `ALLOWED_ORIGINS` in the deployment environment, and use persistent storage for uploaded files and Chroma data.

## Usage

1. Register an account or sign in with email and password.
2. Optionally enroll a face from the browser camera to enable face login.
3. Upload a supported document from the document panel and wait for its status to become `ready`.
4. Select one or more ready documents, then ask a question about their contents. The API returns retrieved source metadata when evidence is found and saves it with the assistant message.
5. Ask a general question without document intent to use the general AI chat path.
6. Reopen, rename, or delete your saved conversations; use the speaker control on an assistant response to read it aloud.

## Technical Highlights

- **Evidence-bound RAG:** document prompts separate recent conversation context from factual evidence and explicitly prohibit unsupported claims.
- **Tenant-aware retrieval:** Chroma metadata includes user and document identifiers; retrieval and document lifecycle operations enforce ownership boundaries.
- **Traceable answers:** retrieved source metadata travels from the vector search result through the API response and persisted message record.
- **Resilient document pipeline:** uploads are validated, processing state is recorded, and failed ingestion cleans up its vectors and stored file where possible.
- **Selective OCR:** digital PDF pages use native extraction; only pages without useful text are rendered and sent to OCR.
- **Lazy heavy dependencies:** the embedding model, Chroma client, Groq chat client, and Whisper model are initialized only when the related capability is used.

## Testing

The repository includes isolated unit and smoke coverage for authentication, documents, RAG retrieval and routing, conversations, OCR, face matching, PostgreSQL adapters, TTS helpers, and application startup.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The current repository checkout completed **58 tests successfully** with this command. The frontend quality checks are:

```powershell
Set-Location Frontend
npm.cmd run lint
npm.cmd run build
```

Both commands completed successfully in the audited checkout.

## Limitations

- Chat generation depends on a valid Groq API key and network access to the provider.
- OCR is English-only in the current implementation and requires Tesseract when scanned/low-text PDF pages need processing.
- The active face-login flow stores one embedding per user and compares it with registered embeddings; it has no liveness detection and is not a high-security biometric system.
- The current UI uses the browser Web Speech API for speech input, so availability varies by browser. Server-side TTS is configured around Windows SAPI/pyttsx3 behavior.
- Document-mode routing uses explicit references, selected documents, and lightweight heuristics; it is not a learned intent classifier.

## Future Improvements

- Add liveness detection, stronger biometric safeguards, and scalable face-search indexing.
- Add asynchronous ingestion with progress reporting for larger document collections.
- Add structured source citations in the UI, evaluation datasets, and retrieval-quality measurements.
- Add multi-language OCR and configurable embedding/LLM providers.
- Add CI automation and redacted UI screenshots.

## Contributors

Git history attributes commits to:

- `mueedahmed-7`
- `NehalKashif`
- `ebrahimkhan-code`
