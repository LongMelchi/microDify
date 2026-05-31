"""Pydantic base schemas for microDify.

Naming convention for all request/response schemas across the project:

    XxxCreate   — request body for POST /<resource>/
    XxxResponse — response body for GET/PATCH /<resource>/<id>
    XxxFilter   — query-string filters for GET /<resource>/

All API endpoints MUST return ``Result[T]`` or ``PageResult[T]``.
"""

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ── Generic type variable ──────────────────────────────────────────────────────

T = TypeVar("T")


# ── Unified API response wrappers ──────────────────────────────────────────────


class Result(BaseModel, Generic[T]):
    """Unified response body returned by every API endpoint.

    Use the class methods for quick construction::

        Result.ok(user)          # → code=200, message="success", data=user
        Result.fail(404, "…")    # → code=404, message="…", data=None
    """

    code: int = Field(default=200, description="HTTP-style status code")
    message: str = Field(default="success", description="Human-readable message")
    data: T | None = Field(default=None, description="Response payload")

    @classmethod
    def ok(cls, data: T | None = None, *, message: str = "success") -> "Result[T]":
        """Build a successful result (code=200)."""
        return cls(code=200, message=message, data=data)

    @classmethod
    def fail(cls, code: int, message: str) -> "Result[None]":
        """Build a failure result with the given error code and message."""
        return cls(code=code, message=message, data=None)


class PageResult(Result[T]):
    """Unified paginated response.

    Inherits ``code``, ``message``, and ``data`` from ``Result``.  ``data`` is
    the list of items for the current page.

    Use the class method for quick construction::

        PageResult.ok(items, total=100, page=1, size=20)
    """

    total: int = Field(..., ge=0, description="Total number of records")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, le=100, description="Number of items per page")

    @classmethod
    def ok(
        cls,
        data: list[T],
        *,
        total: int,
        page: int,
        size: int,
        message: str = "success",
    ) -> "PageResult[T]":
        """Build a successful paginated result (code=200)."""
        return cls(
            code=200,
            message=message,
            data=data,
            total=total,
            page=page,
            size=size,
        )


# ── Pagination ──────────────────────────────────────────────────────────────────


async def paginate(
    db: "AsyncSession",
    stmt,
    *,
    page: int = 1,
    size: int = 20,
) -> PageResult:
    """Execute a paginated query and return a ``PageResult``.

    Uses two queries: a ``COUNT(*)`` for the total, then ``LIMIT / OFFSET`` for
    the current page.  For datasets expected to stay under 100K rows this
    overhead is negligible.

    ``page`` must be >= 1, ``size`` must be between 1 and 100.
    """
    from sqlalchemy import func as sa_func, select

    page = max(page, 1)
    size = max(min(size, 100), 1)

    # ── total count ──────────────────────────────────────────────────────────
    count_stmt = select(sa_func.count()).select_from(stmt.subquery())
    total_row = await db.execute(count_stmt)
    total: int = total_row.scalar_one()

    if total == 0:
        return PageResult.ok([], total=0, page=page, size=size)

    # ── current page ─────────────────────────────────────────────────────────
    rows = await db.execute(stmt.limit(size).offset((page - 1) * size))
    items = list(rows.scalars().all())

    return PageResult.ok(items, total=total, page=page, size=size)


class CoreResponse(BaseModel):
    """Base response schema.

    All response schemas should inherit from this class.  ``from_attributes``
    is enabled so that SQLAlchemy ORM instances can be returned directly.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Resource UUID")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")


class CoreCreate(BaseModel):
    """Base create request schema.

    Inherit from this for POST endpoint request bodies.
    ``from_attributes`` is enabled for convenience during testing/seed data.
    """

    model_config = ConfigDict(from_attributes=True)


class CoreFilter(BaseModel):
    """Base filter schema.

    Inherit from this for GET endpoint query parameters.
    """

    model_config = ConfigDict(from_attributes=True)
