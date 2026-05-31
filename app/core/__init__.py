"""Core module: public infrastructure (config, database, security, exceptions, pagination, logging).

Dependency level: 0 — no external module imports allowed.
"""

from app.core.database import Base, SoftDeleteMixin, TimestampsMixin, get_db
from app.core.exceptions import BizException, ErrorCode
from app.core.schemas import PageResult, Result, paginate
from app.core.service import get_settings

__all__ = [
    "Base",
    "BizException",
    "ErrorCode",
    "PageResult",
    "Result",
    "SoftDeleteMixin",
    "TimestampsMixin",
    "get_db",
    "get_settings",
    "paginate",
]
