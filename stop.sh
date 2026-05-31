#!/usr/bin/env bash
set -euo pipefail

# ── microDify development stopper ─────────────────────────────────────────────
# Usage:  bash stop.sh
#
# What it does:
#   1. Read PID files for backend and frontend (written by start.sh).
#   2. Send SIGTERM and wait up to 10 s for graceful shutdown.
#   3. Force SIGKILL if the process is still alive.
#   4. Fall back to process-name lookup if PID files are missing.

# ── Configuration ──────────────────────────────────────────────────────────────

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$ROOT_DIR/.pids"
BACKEND_FILE="$PID_DIR/backend.pid"
FRONTEND_FILE="$PID_DIR/frontend.pid"
TIMEOUT=10

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ── Helpers ────────────────────────────────────────────────────────────────────

ok()   { echo -e "${GREEN}  ✓${NC} $1"; }
warn() { echo -e "${YELLOW}  !${NC} $1"; }
info() { echo -e "${YELLOW}[stop]${NC} $1"; }

stop_one() {
  local label="$1"
  local pid_file="$2"
  local process_pattern="$3"

  info "Stopping $label..."

  # ── Resolve PID ──────────────────────────────────────────────────────────
  local pid=""
  if [ -f "$pid_file" ] && [ -s "$pid_file" ]; then
    pid="$(cat "$pid_file")"
  fi

  if [ -z "$pid" ] || ! kill -0 "$pid" 2>/dev/null; then
    # Fallback: find by process pattern
    pid=$(ps aux 2>/dev/null | grep "$process_pattern" | grep -v grep | awk '{print $2}' | head -1 || true)
    if [ -z "$pid" ]; then
      warn "$label is not running (no PID found)."
      rm -f "$pid_file"
      return 0
    fi
  fi

  # ── Graceful shutdown (SIGTERM) ──────────────────────────────────────────
  info "Sending SIGTERM to $label (PID $pid)..."
  kill "$pid" 2>/dev/null || true

  local waited=0
  while [ $waited -lt $TIMEOUT ]; do
    if ! kill -0 "$pid" 2>/dev/null; then
      ok "$label stopped gracefully after ${waited}s."
      rm -f "$pid_file"
      return 0
    fi
    sleep 1
    waited=$((waited + 1))
  done

  # ── Force kill (SIGKILL) ─────────────────────────────────────────────────
  warn "$label did not exit within ${TIMEOUT}s — sending SIGKILL."
  kill -9 "$pid" 2>/dev/null || true
  sleep 1

  if ! kill -0 "$pid" 2>/dev/null; then
    ok "$label force-stopped."
  else
    echo -e "${RED}  ✗${NC} Failed to stop $label (PID $pid)."
  fi
  rm -f "$pid_file"
}

# ── Main ───────────────────────────────────────────────────────────────────────

echo ""
info "Looking for microDify processes..."

# Backend — uvicorn / fastapi
stop_one "Backend"  "$BACKEND_FILE"  "[u]vicorn app.main"

# Frontend — next dev
stop_one "Frontend" "$FRONTEND_FILE" "[n]ext dev"

# Cleanup any leftover PID files
rm -f "$BACKEND_FILE" "$FRONTEND_FILE"

echo ""
echo -e "${GREEN}microDify stopped.${NC}"
echo ""
