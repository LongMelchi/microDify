# microDify Makefile — Windows (Git Bash) + Linux compatible
# Usage:  make <target>
#
# Prerequisites: PostgreSQL + Redis running locally (no Docker).
# See .env for connection details.

.PHONY: start stop restart restart-backend build build-backend build-frontend clean clean-backend clean-frontend test db-migrate help

ROOT_DIR  := $(CURDIR)
BACKEND   := $(ROOT_DIR)/app
FRONTEND  := $(ROOT_DIR)/frontend

# Use project venv
VENV_PYTHON := $(ROOT_DIR)/.venv/Scripts/python
VENV_PIP    := $(ROOT_DIR)/.venv/Scripts/pip

# ── Dev server lifecycle ───────────────────────────────────────────────────

start:
	@bash "$(ROOT_DIR)/start.sh"

stop:
	@bash "$(ROOT_DIR)/stop.sh"

restart: stop start

restart-backend:
	@echo "=== Restarting backend only ==="
	@powershell -Command "$$pids=(netstat -ano 2>$$null | Select-String ':8000 ' | Select-String 'LISTENING' | ForEach-Object { (-split $$_.Line)[-1] }); if ($$pids) { $$pids | ForEach-Object { taskkill //PID $$_ //F 2>$$null } }"
	@sleep 1
	"$(VENV_PYTHON)" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# ── Build ──────────────────────────────────────────────────────────────────

build: build-backend build-frontend
	@echo "Build complete."

build-backend:
	@echo "=== Installing Python dependencies (venv) ==="
	"$(VENV_PIP)" install -e "$(ROOT_DIR)[dev]" psycopg2-binary --quiet 2>&1 | tail -1 || true
	"$(VENV_PYTHON)" -c "from app.main import app; print('Backend imports OK')"

build-frontend:
	@echo "=== Building Next.js frontend ==="
	cd "$(FRONTEND)" && npm install --silent && npm run build

# ── Database ───────────────────────────────────────────────────────────────

db-migrate:
	@echo "=== Running database migrations ==="
	"$(VENV_PYTHON)" -m alembic upgrade head

db-migrate-new:
	@echo "=== Generating new migration ==="
	"$(VENV_PYTHON)" -m alembic revision --autogenerate -m "$(msg)"

# ── Clean ──────────────────────────────────────────────────────────────────

clean: clean-backend clean-frontend
	@echo "Clean complete."

clean-backend:
	@echo "=== Cleaning Python artifacts ==="
	find "$(BACKEND)" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find "$(BACKEND)" -type f -name '*.pyc' -delete 2>/dev/null || true

clean-frontend:
	@echo "=== Cleaning Next.js artifacts ==="
	rm -rf "$(FRONTEND)/.next"

# ── Test ───────────────────────────────────────────────────────────────────

test:
	@echo "=== Running backend tests ==="
	"$(VENV_PYTHON)" -m pytest tests/ -v

# ── Help ───────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "microDify Makefile"
	@echo "=================="
	@echo ""
	@echo "Prerequisites: PostgreSQL + Redis running locally"
	@echo "Connection:     postgres:****@localhost:5432/microdify"
	@echo "                redis://localhost:6379/0"
	@echo ""
	@echo "Targets:"
	@echo "  start           Kill old servers + start backend + frontend"
	@echo "  stop            Stop all dev servers (wraps stop.sh)"
	@echo "  restart         Restart all dev servers"
	@echo "  restart-backend Restart backend only (kills port 8000, starts uvicorn --reload)"
	@echo "  build           Install deps (pip + npm) and verify"
	@echo "  build-backend   Install Python deps into .venv/"
	@echo "  build-frontend  npm install && npm run build"
	@echo "  db-migrate      Run Alembic migrations (upgrade head)"
	@echo "  db-migrate-new  Auto-generate a new migration (msg= required)"
	@echo "  clean           Remove build artifacts"
	@echo "  test            Run pytest"
	@echo "  help            Show this help"
	@echo ""
