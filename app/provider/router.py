"""Provider API routes — placeholder, no endpoints defined yet.

Provider configuration (API keys, model selection, rate limits) is managed
through environment variables at startup, not through a REST API.
Management endpoints can be added here when an admin UI is needed.

See CLAUDE.md §4: provider/ does not produce database tables — all config
is loaded from environment via ``app.core.config``.
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/provider",
    tags=["provider"],
)
