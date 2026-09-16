$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Python virtual environment not found at .venv. Follow LOCAL_SETUP.md first."
}

Set-Location $projectRoot
& $python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
