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

# ── Step 1 — Ensure PostgreSQL is running ──────────────────────────────────────

step "Checking PostgreSQL..."

# Try to source db credentials from .env if present
if [ -f "$ROOT_DIR/.env" ]; then
  set -a; source "$ROOT_DIR/.env"; set +a
fi

PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"

ensure_pg() {
  # Already running?
  if command -v pg_isready &>/dev/null; then
    if pg_isready -h "$PG_HOST" -p "$PG_PORT" -q 2>/dev/null; then
      ok "PostgreSQL is ready"
      return 0
    fi
  fi
  # Windows: start the PostgreSQL service
  if command -v sc &>/dev/null; then
    step "PostgreSQL not running — starting service..."
    sc start postgresql-x64-18 2>/dev/null || true
    # Wait for it
    for i in $(seq 1 15); do
      if command -v pg_isready &>/dev/null; then
        pg_isready -h "$PG_HOST" -p "$PG_PORT" -q 2>/dev/null && break
      fi
      sleep 1
    done
    if pg_isready -h "$PG_HOST" -p "$PG_PORT" -q 2>/dev/null; then
      ok "PostgreSQL started"
      return 0
    fi
  fi
  die "PostgreSQL is NOT reachable at ${PG_HOST}:${PG_PORT}. Start it manually."
}
ensure_pg

# ── Step 2 — Ensure Redis is running ──────────────────────────────────────────

step "Checking Redis..."

REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

# Try known Redis install locations
REDIS_SERVER=""
for candidate in \
  "D:/redis/Redis-x64-5.0.14.1/redis-server.exe" \
  "E:/redis/Redis-x64-5.0.14.1/redis-server.exe" \
  "C:/redis/Redis-x64-5.0.14.1/redis-server.exe"; do
  if [ -f "$candidate" ]; then
    REDIS_SERVER="$candidate"
    break
  fi
done

ensure_redis() {
  # Already running?
  if command -v redis-cli &>/dev/null; then
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" PING 2>/dev/null | grep -q PONG; then
      ok "Redis is ready"
      return 0
    fi
  fi
  # Auto-start if redis-server found
  if [ -n "$REDIS_SERVER" ]; then
    step "Redis not running — starting..."
    "$REDIS_SERVER" --port "$REDIS_PORT" --maxmemory 128mb &
    # Wait up to 5 s for it to be ready
    for i in $(seq 1 5); do
      sleep 1
      if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" PING 2>/dev/null | grep -q PONG; then
        ok "Redis started"
        return 0
      fi
    done
    # Port might already be in use by another Redis instance
    if (netstat -ano 2>/dev/null | grep ":${REDIS_PORT} " | grep -q LISTENING); then
      ok "Redis port is occupied (already running)"
      return 0
    fi
  fi
  die "Redis is NOT reachable at ${REDIS_HOST}:${REDIS_PORT}. Start it manually."
}
ensure_redis

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
