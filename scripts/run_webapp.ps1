<#
.SYNOPSIS
    Single-command local launcher for Project 12 Standalone Web Application (FastAPI + React).

.DESCRIPTION
    Production mode (default): ensures backend requirements and built frontend assets
    exist, then serves both REST API and static SPA on http://127.0.0.1:8000.

    Dev mode (-Dev): starts Uvicorn with --reload on port 8000 alongside Vite HMR dev server
    on http://127.0.0.1:5173.
#>
[CmdletBinding()]
param(
    [int]$Port = 8000,
    [switch]$Dev,
    [switch]$Rebuild
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$FrontendDir = Join-Path $RepoRoot "webapp\frontend"
$DistIndex = Join-Path $FrontendDir "dist\index.html"
$BackendReqs = Join-Path $RepoRoot "webapp\backend\requirements.txt"

if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment python not found at '$PythonExe'. Create .venv and install requirements first."
}

& $PythonExe -c "import fastapi, uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing FastAPI backend dependencies into .venv..."
    & $PythonExe -m pip install -r $BackendReqs
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install backend dependencies."
    }
}

Push-Location $RepoRoot
try {
    if ($Dev) {
        if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
            Write-Host "Installing frontend packages..."
            npm --prefix $FrontendDir install
            if ($LASTEXITCODE -ne 0) { throw "npm install failed." }
        }

        Write-Host "Starting FastAPI backend (reload) on http://127.0.0.1:$Port ..."
        $BackendProc = Start-Process -FilePath $PythonExe -ArgumentList @(
            "-m", "uvicorn", "webapp.backend.main:app",
            "--host", "127.0.0.1", "--port", "$Port", "--reload"
        ) -WorkingDirectory $RepoRoot -PassThru

        try {
            Write-Host "Starting Vite dev server on http://127.0.0.1:5173 (proxying /api -> :$Port) ..."
            npm --prefix $FrontendDir run dev
        }
        finally {
            if ($BackendProc -and -not $BackendProc.HasExited) {
                Stop-Process -Id $BackendProc.Id -Force
            }
        }
    }
    else {
        if ($Rebuild -or -not (Test-Path $DistIndex)) {
            if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
                Write-Host "Installing frontend packages..."
                npm --prefix $FrontendDir install
                if ($LASTEXITCODE -ne 0) { throw "npm install failed." }
            }
            Write-Host "Building production React SPA bundle..."
            npm --prefix $FrontendDir run build
            if ($LASTEXITCODE -ne 0) { throw "Frontend build failed." }
        }

        Write-Host ""
        Write-Host "HANU Campus Notice & FAQ Assistant is starting:"
        Write-Host "  Web UI : http://127.0.0.1:$Port"
        Write-Host "  API Doc: http://127.0.0.1:$Port/docs"
        Write-Host ""
        & $PythonExe -m uvicorn webapp.backend.main:app --host 127.0.0.1 --port $Port
    }
}
finally {
    Pop-Location
}
