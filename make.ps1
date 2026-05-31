# microDify — PowerShell launcher for Windows
# Usage:  .\make.ps1 <target>
#
# Prerequisites: PostgreSQL 18 + Redis running locally.
# Connection: postgres:****@localhost:5432/microdify
#             redis://localhost:6379/0

param([string]$Target = "help")

$Root    = $PSScriptRoot
$Bash    = "E:\Program Files\Git\bin\bash.exe"
$Start   = Join-Path $Root "start.sh"
$Stop    = Join-Path $Root "stop.sh"
$VenvPy  = Join-Path $Root ".venv\Scripts\python.exe"
$VenvPip = Join-Path $Root ".venv\Scripts\pip.exe"

function Free-Port($Port) {
  $portPid = (netstat -ano 2>$null | Select-String ":$Port " | Select-String "LISTENING" | ForEach-Object { (-split $_.Line)[-1] } | Select-Object -First 1)
  if ($portPid) {
    Write-Host "Port $Port in use (PID $portPid) — killing..." -ForegroundColor Yellow
    taskkill //PID $portPid //F 2>$null | Out-Null
    Write-Host "  Port $Port freed" -ForegroundColor Green
  }
}

function Run-Bash($ScriptPath) {
  if (-not (Test-Path $Bash)) {
    Write-Host "[ERROR] Git Bash not found at: $Bash" -ForegroundColor Red
    exit 1
  }
  & $Bash $ScriptPath
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

switch ($Target) {
  "start" {
    Write-Host "Checking ports 8000, 3000..." -ForegroundColor Yellow
    Free-Port 8000
    Free-Port 3000
    Write-Host "Starting microDify (local PG + Redis)..." -ForegroundColor Yellow
    Run-Bash $Start
  }
  "stop" {
    Write-Host "Stopping microDify..." -ForegroundColor Yellow
    Free-Port 8000
    Free-Port 3000
    Run-Bash $Stop
  }
  "restart" {
    Run-Bash $Stop
    Start-Sleep -Seconds 1
    Free-Port 8000
    Free-Port 3000
    Run-Bash $Start
  }
  "build" {
    Write-Host "=== Building backend (.venv) ===" -ForegroundColor Yellow
    & $VenvPip install -e "$Root[dev]" psycopg2-binary --quiet 2>&1 | Select-Object -Last 3
    & $VenvPy -c "from app.main import app; print('Backend OK')"
    Write-Host "=== Building frontend ===" -ForegroundColor Yellow
    Push-Location "$Root\frontend"
    npm install --silent
    npm run build
    Pop-Location
    Write-Host "Build complete." -ForegroundColor Green
  }
  "build-backend" {
    Write-Host "=== Installing Python deps into .venv/ ===" -ForegroundColor Yellow
    & $VenvPip install -e "$Root[dev]" psycopg2-binary --quiet
    & $VenvPy -c "from app.main import app; print('Backend OK')"
  }
  "build-frontend" {
    Write-Host "=== Building Next.js frontend ===" -ForegroundColor Yellow
    Push-Location "$Root\frontend"
    npm install --silent
    npm run build
    Pop-Location
    Write-Host "Frontend OK." -ForegroundColor Green
  }
  "db-migrate" {
    Write-Host "=== Running Alembic migrations ===" -ForegroundColor Yellow
    & $VenvPy -m alembic upgrade head
  }
  "db-migrate-new" {
    param([string]$msg = "auto")
    Write-Host "=== Generating migration: $msg ===" -ForegroundColor Yellow
    & $VenvPy -m alembic revision --autogenerate -m $msg
  }
  "clean" {
    Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
    Get-ChildItem -Path $Root -Recurse -Directory -Name "__pycache__" | ForEach-Object {
      Remove-Item -Recurse -Force (Join-Path $Root $_) -ErrorAction SilentlyContinue
    }
    Remove-Item -Recurse -Force "$Root\frontend\.next" -ErrorAction SilentlyContinue
    Write-Host "Clean complete." -ForegroundColor Green
  }
  "test" {
    & $VenvPy -m pytest "$Root\tests" -v
  }
  "help" {
    Write-Host @"

microDify (PowerShell launcher)
===============================
Prerequisites: PostgreSQL 18 + Redis running locally
Connection:     postgres:****@localhost:5432/microdify
                redis://localhost:6379/0

Usage:  .\make.ps1 <target>

Targets:
  start           Start backend + frontend dev servers
  stop            Stop all dev servers
  restart         Restart all dev servers
  build           Install deps (pip into .venv/ + npm) and verify
  build-backend   Install Python deps into .venv/
  build-frontend  npm install, npm run build
  db-migrate      Run Alembic migrations (upgrade head)
  db-migrate-new  Auto-generate migration (-msg "description")
  clean           Remove __pycache__, .pyc, .next
  test            Run pytest
  help            Show this help
"@
  }
  default {
    Write-Host "Unknown target: $Target. Use 'help' to see available targets." -ForegroundColor Red
    exit 1
  }
}
