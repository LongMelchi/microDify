"""Base SQLAlchemy models for the common module.

All model classes defined here are **abstract** — their ``__tablename__``
will be set by concrete subclasses (or the modules that use them).

Inherits from :class:`app.core.database.Base` (the global declarative base
shared by all microDify modules).
"""

from app.core.database import Base


class FileRecord(Base):
    """Abstract base for uploaded-file storage records.

    Concrete subclasses should set ``__tablename__`` (e.g. ``"uploaded_files"``)
    and add columns specific to the file type (path, size, mime_type, …).
    """

    __abstract__ = True


class QueueTask(Base):
    """Abstract base for async queue task records.

    Concrete subclasses should set ``__tablename__`` (e.g. ``"queue_tasks"``)
    and add columns for task type, status, payload, result, etc.
    """

    __abstract__ = True


class RateLimitLog(Base):
    """Abstract base for rate-limit audit / counter records.

    Concrete subclasses should set ``__tablename__`` (e.g. ``"rate_limit_logs"``)
    and add columns for user_id, endpoint, window_start, count, etc.
    """

    __abstract__ = True


class EventLog(Base):
    """Abstract base for event bus audit records.

    Concrete subclasses should set ``__tablename__`` (e.g. ``"event_logs"``)
    and add columns for event_type, payload, source, created_at, etc.
    """

    __abstract__ = True
