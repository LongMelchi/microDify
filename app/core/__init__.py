"""Core module: public infrastructure (config, database, security, exceptions, pagination, logging).

Dependency level: 0 — no external module imports allowed.
"""

from app.core.database import Base, SoftDeleteMixin, TimestampsMixin, get_db
from app.core.deps import get_current_user_id
from app.core.exceptions import BizException, ErrorCode
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.schemas import PageResult, Result, paginate
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.core.service import get_settings

__all__ = [
    "Base",
    "BizException",
    "ErrorCode",
    "PageResult",
    "RequestLoggingMiddleware",
    "Result",
    "SoftDeleteMixin",
    "TimestampsMixin",
    "create_token",
    "decode_token",
    "get_current_user_id",
    "get_db",
    "get_settings",
    "hash_password",
    "paginate",
    "setup_logging",
    "verify_password",
]
