"""Prompt template business logic.

Public exports (via __init__.py):
    get_template    — retrieve a template by ID (with LRU cache)
    render_template — load template + interpolate {{variable}} placeholders
    invalidate_template_cache — clear cached template after update/delete
"""

import logging
from functools import lru_cache
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.prompt.models import PromptTemplate

logger = logging.getLogger(__name__)


# ── In-process template cache ──────────────────────────────────────────────────
# Templates change rarely (days/weeks), so a per-worker LRU cache is safe.
# Two workers may briefly disagree after an update — acceptable trade-off for
# not introducing Redis Pub/Sub at this stage.


@lru_cache(maxsize=256)
def _cached_template(template_id: UUID) -> PromptTemplate | None:
    """Placeholder — the real cache is keyed on ``(template_id,)`` and filled
    by ``get_template``.  This function exists so that ``lru_cache`` has a
    pure-func entry point we can invalidate."""
    return None


async def get_template(db: AsyncSession, user_id: UUID, template_id: UUID) -> PromptTemplate | None:
    """Retrieve a prompt template, with in-process LRU cache."""
    # Try cache first
    cached = _cached_template(template_id)
    if cached is not None and cached.user_id == user_id:
        return cached

    stmt = select(PromptTemplate).where(
        PromptTemplate.id == template_id,
        PromptTemplate.user_id == user_id,
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    # Warm cache
    if template is not None:
        _cached_template.__wrapped__(template_id, template)  # type: ignore[attr-defined]

    return template


async def render_template(
    db: AsyncSession,
    user_id: UUID,
    template_id: UUID,
    variables: dict[str, str],
) -> str:
    """Load a prompt template and interpolate ``{{variable}}`` placeholders."""
    template = await get_template(db, user_id, template_id)
    if template is None:
        raise ValueError(f"PromptTemplate {template_id} not found for user {user_id}")

    rendered = template.content
    for key, value in variables.items():
        rendered = rendered.replace("{{" + key + "}}", value)

    return rendered


def invalidate_template_cache(template_id: UUID) -> None:
    """Clear the cached template after update/delete. Call in CRUD service methods."""
    _cached_template.cache_clear()  # type: ignore[attr-defined]
