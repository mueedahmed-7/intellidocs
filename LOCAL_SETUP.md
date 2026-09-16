# IntelliDocs local setup (Windows PowerShell)

This runs IntelliDocs entirely on your PC. It does not deploy anything and uses local PostgreSQL, local uploads, and local Chroma storage.

## First-time setup

1. **[FOLDER]** Open PowerShell in the project folder:

   **[COMMAND]**
   ```powershell
   cd "C:\Users\Mueed Ahmed\Desktop\AI-Powered-Rag-Chatbot"
   ```

2. **[COMMAND]** Create and activate a Python 3.13 virtual environment:

   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation for your user, run `Set-ExecutionPolicy -Scope Process Bypass` once in that terminal, then activate again.

3. **[COMMAND]** Install backend packages:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. **[COMMAND]** Create the PostgreSQL database (only if it does not already exist). Enter your PostgreSQL password only when `psql` prompts for it:

   ```powershell
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres -c "CREATE DATABASE intellidocs;"
   ```

   If PostgreSQL reports that `intellidocs` already exists, that is safe—continue. This project never drops, truncates, or resets a database.

5. **[FILE]** Create the backend configuration from the safe template:

   **[COMMAND]**
   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```

   Set `DATABASE_URL` using your real PostgreSQL username and password, set a long random `JWT_SECRET_KEY`, and set `GROQ_API_KEY`. Keep `PERSISTENT_DATA_DIR=data`. If Tesseract is installed but not on PATH, uncomment/set `TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe`.

6. **[COMMAND]** Create required tables without altering existing rows:

   ```powershell
   .\.venv\Scripts\python.exe -m backend.scripts.init_db
   ```

7. **[FOLDER]** Configure and install the Vite frontend:

   **[COMMAND]**
   ```powershell
   cd .\Frontend
   Copy-Item .env.example .env
   npm.cmd install
   cd ..
   ```

   `Frontend\.env` should contain `VITE_API_BASE_URL=http://127.0.0.1:8000`.

## Everyday startup

Open two PowerShell terminals in the project folder.

**Terminal 1 — backend**

```powershell
.\scripts\start-backend.ps1
```

**Terminal 2 — frontend**

```powershell
.\scripts\start-frontend.ps1
```

Open [http://localhost:5173](http://localhost:5173). The backend health check is [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

## Storage and behavior

- **[FOLDER]** Uploads: `data\uploads\`
- **[FOLDER]** Chroma vectors: `data\chroma_db\`
- **[DATABASE]** PostgreSQL: `intellidocs` (users, documents, chats, messages, face embeddings)
- Digital PDFs use native text extraction first. Tesseract OCR is used only for scanned/low-text PDF pages.
- New accounts go to required browser-based face registration before chat. Localhost is a trusted development context for webcam access; allow camera permission in the browser.

## Shutdown

Press `Ctrl+C` in each terminal.

## Troubleshooting

- **Cannot connect / Failed to fetch:** start Terminal 1 and open `/health`; check that `Frontend\.env` has `VITE_API_BASE_URL=http://127.0.0.1:8000`.
- **PostgreSQL is not running:** start the PostgreSQL 18 Windows service, then retry `python -m backend.scripts.init_db`.
- **Wrong `DATABASE_URL`:** check the PostgreSQL username, password, port, and database name. Use `postgresql+psycopg://...` or `postgresql://...`.
- **Missing Groq key:** generic and document chat need a valid `GROQ_API_KEY` in root `.env`; health does not.
- **Webcam denied:** use `http://localhost:5173`, allow camera permission, and close other apps using the camera.
- **Tesseract missing:** normal text PDFs still work. For scanned PDFs, install Tesseract and set `TESSERACT_CMD` in root `.env`.
- **Port already in use:** stop the process already using port 8000 or 5173, or choose another port and update `VITE_API_BASE_URL` plus `ALLOWED_ORIGINS` consistently.
