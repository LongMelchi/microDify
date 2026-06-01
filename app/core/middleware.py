"""ASGI middleware — request logging with ``request_id`` propagation + runtime metrics.

Usage in ``main.py``::

    from app.core.middleware import RequestLoggingMiddleware, get_metrics
    app.add_middleware(RequestLoggingMiddleware)
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import Counter

import structlog

from app.core.logging import request_id_var

logger = structlog.get_logger("microdify.access")

# ── Runtime metrics ────────────────────────────────────────────────────────────

_metrics_lock = threading.Lock()
_started_at: float | None = None  # set on first request or explicitly by main.py
_total_requests: int = 0
_status_counts: Counter[str] = Counter()
_active_sse: int = 0


def mark_started() -> None:
    """Record the application start time.  Called from ``main.py`` lifespan."""
    global _started_at
    _started_at = time.monotonic()


def get_metrics() -> dict:
    """Return a snapshot of runtime metrics (thread-safe)."""
    with _metrics_lock:
        total = _total_requests
        status = dict(_status_counts)
        sse = _active_sse
        uptime = (
            round(time.monotonic() - _started_at, 1) if _started_at else 0.0
        )
    errors = sum(v for k, v in status.items() if k.startswith("5") or k.startswith("4"))
    return {
        "uptime_seconds": uptime,
        "total_requests": total,
        "active_sse_connections": sse,
        "status_counts": status,
        "error_count": errors,
    }


# ── Middleware ─────────────────────────────────────────────────────────────────


class RequestLoggingMiddleware:
    """Logs every HTTP request and tracks runtime counters."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        # Only wrap HTTP requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # --- request_id -----------------------------------------------------
        raw_headers = dict(scope.get("headers", []))
        incoming = raw_headers.get(b"x-request-id")
        rid = incoming.decode() if incoming else uuid.uuid4().hex[:8]
        token = request_id_var.set(rid)

        # --- timing ---------------------------------------------------------
        start = time.monotonic()
        status_code = 500
        is_sse = False

        # --- wrapped send ---------------------------------------------------
        async def send_wrapper(message):
            nonlocal status_code, is_sse
            global _active_sse
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", rid.encode()))
                # Detect SSE
                for k, v in headers:
                    if k.lower() == b"content-type" and b"text/event-stream" in v.lower():
                        is_sse = True
                        with _metrics_lock:
                            _active_sse += 1
                message["headers"] = headers
            await send(message)

            # SSE connection closed
            if is_sse and message["type"] == "http.response.body" and not message.get("more_body", False):
                with _metrics_lock:
                    _active_sse = max(0, _active_sse - 1)

        # --- counter --------------------------------------------------------
        global _total_requests, _started_at
        with _metrics_lock:
            if _started_at is None:
                _started_at = start  # lazy init on first request
            _total_requests += 1

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            status_code = 500
            raise
        finally:
            with _metrics_lock:
                _status_counts[str(status_code)] += 1

            elapsed_ms = (time.monotonic() - start) * 1000
            logger.info(
                "request",
                method=scope.get("method", ""),
                path=scope.get("path", ""),
                status=status_code,
                duration_ms=round(elapsed_ms, 2),
            )
            request_id_var.reset(token)
