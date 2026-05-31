"""Base SQLAlchemy models for microDify.

All business module model classes should inherit from ``CoreModel``
and set ``__tablename__`` explicitly in their own ``models.py``.

Example::

    from app.core.models import CoreModel

    class ChatApp(CoreModel):
        __tablename__ = "chat_apps"
        name = Column(String, nullable=False)
"""

import uuid

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class CoreModel(Base):
    """Abstract base model providing a UUID primary key and timestamp columns.

    Columns provided:
        id          — UUID primary key (auto-generated via Python uuid.uuid4)
        created_at  — UTC timestamp, set on insert (server default NOW())
        updated_at  — UTC timestamp, updated on every row modification
    """

    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
