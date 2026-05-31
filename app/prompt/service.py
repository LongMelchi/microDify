# prompt/service.py
# Business logic for the prompt module.
# Pure async functions — signature only accepts db/user/business parameters.
# Never receives Request, Response, or BackgroundTasks objects.
# Max 400 lines; extract helper modules (e.g. renderer.py) when exceeded.
#
# Allowed cross-module imports per CLAUDE.md §2:
#   core, auth

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.prompt.models import PromptTemplate

logger = logging.getLogger(__name__)


async def get_template(db: AsyncSession, user_id: UUID, template_id: UUID) -> PromptTemplate | None:
    """Retrieve a single prompt template by ID, scoped to the owning user.

    Args:
        db: Database session.
        user_id: UUID of the requesting user (authorization scope).
        template_id: UUID of the template to fetch.

    Returns:
        The PromptTemplate ORM instance, or None if not found.
    """
    stmt = select(PromptTemplate).where(
        PromptTemplate.id == template_id,
        PromptTemplate.user_id == user_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def render_template(
    db: AsyncSession,
    user_id: UUID,
    template_id: UUID,
    variables: dict[str, str],
) -> str:
    """Load a prompt template and interpolate ``{{variable}}`` placeholders.

    Args:
        db: Database session.
        user_id: UUID of the requesting user (authorization scope).
        template_id: UUID of the template to render.
        variables: Dict mapping placeholder names to replacement values.

    Returns:
        The fully rendered template string with all placeholders replaced.

    Raises:
        ValueError: If the template is not found.
        KeyError: If a placeholder in the template has no corresponding
            variable provided (TODO: decide strict vs. lenient mode).
    """
    template = await get_template(db, user_id, template_id)
    if template is None:
        raise ValueError(f"PromptTemplate {template_id} not found for user {user_id}")

    rendered = template.content
    for key, value in variables.items():
        rendered = rendered.replace("{{" + key + "}}", value)

    # TODO: Log unmatched placeholders (those still containing {{...}} after replacement)
    # based on final decision about strict vs. lenient mode.

    return rendered
