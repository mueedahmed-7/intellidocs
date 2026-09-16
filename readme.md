# IntelliDocs

IntelliDocs is a local-first document intelligence application. It combines a React/Vite interface with a FastAPI backend, PostgreSQL, Chroma, document RAG, browser voice input, local Windows text-to-speech, and required face registration.

## Features

- Secure account registration, JWT sessions, and required face registration/login.
- Upload and privately index PDF, DOCX, TXT, and Markdown documents.
- Document-grounded RAG answers for selected documents.
- General AI chat for non-document questions.
- Native text extraction with OCR fallback for scanned PDFs.
- Browser speech-to-text and local Windows text-to-speech.
- Persistent PostgreSQL metadata, local uploads, and local Chroma vectors.

## Architecture

```text
React/Vite browser
        |
     FastAPI
   /    |    \
PostgreSQL  local uploads  Chroma vectors
        |
  Groq chat model / local face and OCR services
```

## Local setup

This repository intentionally contains no credentials, personal documents, vector databases, or biometric records. See [LOCAL_SETUP.md](LOCAL_SETUP.md) for the complete Windows PowerShell setup guide.

Quick start after first-time setup:

```powershell
# Terminal 1
.\scripts\start-backend.ps1

# Terminal 2
.\scripts\start-frontend.ps1
```

Open `http://localhost:5173`.

## Configuration

Copy the provided examples; never commit real `.env` files:

```powershell
Copy-Item .env.example .env
Copy-Item Frontend\.env.example Frontend\.env
```

Required backend configuration includes:

- `DATABASE_URL` — local PostgreSQL database connection.
- `JWT_SECRET_KEY` — long random signing secret.
- `GROQ_API_KEY` — required for chat generation.
- `PERSISTENT_DATA_DIR=data` — local uploads and Chroma data.

## Data and privacy

The following are deliberately ignored by Git:

- `.env` files and credentials
- Uploaded documents
- Chroma/vector databases
- PostgreSQL data
- Face embeddings and local face data
- Temporary logs

Do not add real user documents, database dumps, tokens, private keys, or biometric data to Git.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v

cd Frontend
npm.cmd run lint
npm.cmd run build
```

## Security note

Face authentication is a convenience feature, not a high-security biometric or liveness-detection system. Use strong passwords, keep secrets outside Git, and rotate any key immediately if it is ever exposed.
