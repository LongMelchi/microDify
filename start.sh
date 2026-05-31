#!/usr/bin/env bash
set -euo pipefail

# ── microDify development launcher ─────────────────────────────────────────────
# Usage:  bash start.sh
#
# What it does:
#   1. Verify PostgreSQL and Redis are reachable.
#   2. Install Python dependencies (if needed).
#   3. Start the FastAPI backend in the background.
#   4. Poll /health until the backend responds.
#   5. Start the Next.js frontend in the foreground.
#   6. On exit (Ctrl+C), gracefully stop the backend.
#
# Prerequisites (start these first, e.g. via docker compose up -d pg redis):
#   - PostgreSQL 16 + pgvector on localhost:5432
#   - Redis 7 on localhost:6379

# ── Configuration ──────────────────────────────────────────────────────────────

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
HEALTH_URL="http://localhost:${BACKEND_PORT}/health"
PID_DIR="$ROOT_DIR/.pids"

mkdir -p "$PID_DIR"
BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"

# Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cleanup() {
  echo ""
  echo -e "${YELLOW}Shutting down...${NC}"
  if [ -n "${BACKEND_PID:-}" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
    echo -e "${GREEN}Backend stopped.${NC}"
  fi
  if [ -n "${FRONTEND_PID:-}" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
    wait "$FRONTEND_PID" 2>/dev/null || true
  fi
  rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"
  exit 0
}
trap cleanup SIGINT SIGTERM

die() {
  echo -e "${RED}[ERROR]${NC} $1"
  exit 1
}

step() {
  echo -e "${YELLOW}[$(date +%H:%M:%S)]${NC} $1"
}

ok() {
  echo -e "${GREEN}  ✓${NC} $1"
}

# ── Step 0 — Clear ports ────────────────────────────────────────────────────────

free_port() {
  local port="$1"
  local pids=""
  # Windows: netstat + taskkill
  if command -v netstat &>/dev/null && command -v taskkill &>/dev/null; then
    pids=$(netstat -ano 2>/dev/null | grep ":${port} " | grep LISTENING | awk '{print $NF}' || true)
    if [ -n "$pids" ]; then
      for pid in $pids; do
        step "Port ${port} is in use (PID ${pid}) — killing..."
        taskkill //PID "$pid" //F 2>/dev/null || true
      done
      ok "Port ${port} freed"
    fi
  # Linux/Mac: lsof + kill
  elif command -v lsof &>/dev/null; then
    pids=$(lsof -ti ":${port}" 2>/dev/null || true)
    if [ -n "$pids" ]; then
      for pid in $pids; do
        step "Port ${port} is in use (PID ${pid}) — killing..."
        kill -9 "$pid" 2>/dev/null || true
      done
      ok "Port ${port} freed"
    fi
  fi
}

step "Checking ports ${BACKEND_PORT} and ${FRONTEND_PORT}..."
free_port "$BACKEND_PORT"
free_port "$FRONTEND_PORT"

# ── Step 1 — Check PostgreSQL ──────────────────────────────────────────────────

step "Checking PostgreSQL..."

# Try to source db credentials from .env if present
if [ -f "$ROOT_DIR/.env" ]; then
  set -a; source "$ROOT_DIR/.env"; set +a
fi

PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"
PG_USER="${POSTGRES_USER:-microdify}"
PG_DB="${POSTGRES_DB:-microdify}"

if command -v pg_isready &>/dev/null; then
  if pg_isready -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -q; then
    ok "PostgreSQL is ready"
  else
    die "PostgreSQL is NOT reachable at ${PG_HOST}:${PG_PORT}. Start it first."
  fi
else
  # Fallback: nc / bash tcp check
  if (echo >/dev/tcp/"$PG_HOST"/"$PG_PORT") 2>/dev/null; then
    ok "PostgreSQL port is open (pg_isready not found, tcp check only)"
  else
    die "PostgreSQL port ${PG_PORT} is NOT open. Start it first."
  fi
fi

# ── Step 2 — Check Redis ───────────────────────────────────────────────────────

step "Checking Redis..."

REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

if command -v redis-cli &>/dev/null; then
  if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" PING | grep -q PONG; then
    ok "Redis is ready"
  else
    die "Redis is NOT reachable at ${REDIS_HOST}:${REDIS_PORT}. Start it first."
  fi
else
  if (echo >/dev/tcp/"$REDIS_HOST"/"$REDIS_PORT") 2>/dev/null; then
    ok "Redis port is open (redis-cli not found, tcp check only)"
  else
    die "Redis port ${REDIS_PORT} is NOT open. Start it first."
  fi
fi

# ── Step 3 — Install Python dependencies ───────────────────────────────────────

step "Installing Python dependencies..."
cd "$ROOT_DIR"

# Use project venv if present
if [ -f ".venv/Scripts/pip" ]; then
  VENV_PYTHON=".venv/Scripts/python"
  VENV_PIP=".venv/Scripts/pip"
elif [ -f ".venv/bin/pip" ]; then
  VENV_PYTHON=".venv/bin/python"
  VENV_PIP=".venv/bin/pip"
else
  VENV_PYTHON="python"
  VENV_PIP="pip"
fi

"$VENV_PIP" install -e ".[dev]" psycopg2-binary --quiet 2>&1 | tail -1 || true
ok "Dependencies ready"

# ── Step 4 — Start backend ─────────────────────────────────────────────────────

step "Starting FastAPI backend on port ${BACKEND_PORT}..."
cd "$ROOT_DIR"

"$VENV_PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --workers 1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$BACKEND_PID_FILE"

# ── Step 5 — Wait for backend health ──────────────────────────────────────────

step "Waiting for backend to become healthy..."
MAX_WAIT=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_WAIT ]; do
  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    die "Backend process exited unexpectedly. Check logs above."
  fi

  HEALTH_RESP=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" 2>/dev/null || echo "000")

  if [ "$HEALTH_RESP" = "200" ]; then
    ok "Backend is healthy (${HEALTH_URL})"
    break
  fi

  ATTEMPT=$((ATTEMPT + 1))
  sleep 1
done

if [ $ATTEMPT -ge $MAX_WAIT ]; then
  die "Backend did not become healthy within ${MAX_WAIT}s."
fi

# ── Step 6 — Start frontend ────────────────────────────────────────────────────

step "Starting Next.js frontend on port ${FRONTEND_PORT}..."
cd "$ROOT_DIR/frontend"

if [ ! -d "node_modules" ]; then
  step "Installing frontend dependencies..."
  npm install --silent || die "npm install failed."
  ok "Frontend dependencies ready"
fi

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  microDify is starting up${NC}"
echo -e "${GREEN}  Backend:  http://localhost:${BACKEND_PORT}${NC}"
echo -e "${GREEN}  Frontend: http://localhost:${FRONTEND_PORT}${NC}"
echo -e "${GREEN}  Press Ctrl+C to stop both services${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo ""

npm run dev -- -p "$FRONTEND_PORT"

# ── Cleanup (triggered by trap on Ctrl+C) ────────────────────────────────────
