$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$frontend = Join-Path $projectRoot "Frontend"

if (-not (Test-Path -LiteralPath (Join-Path $frontend "node_modules"))) {
    throw "Frontend dependencies are not installed. Run npm install in the Frontend folder first."
}

Set-Location $frontend
npm.cmd run dev -- --host localhost --port 5173 --strictPort
