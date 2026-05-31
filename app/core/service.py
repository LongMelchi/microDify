"""Core service layer — pure async infrastructure services.

All functions in this module are async stubs.  They accept only
standard Python parameters (db session, user id, business values)
and never touch Request / Response / BackgroundTasks.
"""

from uuid import UUID


async def get_settings(user_id: UUID | None = None) -> dict:
    """Return application settings, optionally scoped to a user.

    Delegates to ``app.core.config`` for the canonical settings object.
    The ``user_id`` parameter is reserved for future per-user overrides
    (e.g. feature flags, model preferences).

    Args:
        user_id: Optional UUID of the requesting user.

    Returns:
        Flat dictionary of current configuration values.
    """
    # Lazy import to avoid circular dependency at module level —
    # app.core.config is always resolved at call time.
    from app.core.config import get_settings as load_config

    settings = load_config()
    return settings.model_dump()
