"""Structured logging configuration for microDify.

Call ``setup_logging()`` once at application startup (in ``main.py`` lifespan).
"""

import logging
import sys
from contextvars import ContextVar

import structlog

# Shared context variable — middleware writes to this, logger reads from it.
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


def setup_logging(*, debug: bool = False) -> None:
    """Configure structlog for the entire application.

    Args:
        debug: When ``True``, use coloured console output.  Otherwise JSON.
    """
    # Standard-library bridge: redirect stdlib logs to structlog
    logging.basicConfig(format="%(message)s", stream=sys.stderr, level=logging.INFO)

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if debug:
        # Development: coloured console
        structlog.configure(
            processors=shared_processors
            + [
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Production: JSON for log aggregation
        structlog.configure(
            processors=shared_processors
            + [
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )

    # Silence noisy libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
