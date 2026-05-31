"""Database engine, session factory, mixins, and declarative base.

Usage::

    from app.core.database import Base, get_db, TimestampsMixin, SoftDeleteMixin

    class MyModel(Base, TimestampsMixin, SoftDeleteMixin):
        __tablename__ = "my_table"
        ...

Alembic migrations import ``Base`` from this module to discover all ORM models.
"""

from collections.abc import AsyncGenerator
from datetime import datetime

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=5,
    echo=settings.debug,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Mixins ──────────────────────────────────────────────────────────────────────


class TimestampsMixin:
    """Mixin that adds automatic ``created_at`` and ``updated_at`` columns.

    All business models should inherit from this mixin so that timestamps are
    managed consistently by the database server.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin that adds a soft-delete column.

    Models that need soft-delete should inherit from this mixin.  Services are
    responsible for adding ``WHERE is_deleted = FALSE`` to queries — there is no
    global filter interceptor in SQLAlchemy.
    """

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=func.false(),
        nullable=False,
    )


# ── Declarative base ───────────────────────────────────────────────────────────


class Base(DeclarativeBase):
    """Declarative base for all ORM models.

    Every model in the project should inherit from this class or from
    ``CoreModel`` (which itself inherits from ``Base``).
    """

    pass


# ── Session dependency ─────────────────────────────────────────────────────────


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yield a database session for the request lifetime.

    Commits on success, rolls back on exception.  Use as a FastAPI
    ``Depends``::

        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
