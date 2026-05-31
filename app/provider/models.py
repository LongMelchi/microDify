"""Provider ORM models.

Provider configuration is managed entirely through environment variables
and runtime settings.  Per CLAUDE.md §4, this module intentionally produces
**no database tables** — LLM provider configs (API keys, model names,
endpoints, rate limits) are loaded at startup via ``app.core.config`` and
never persisted to PostgreSQL.

If a future admin feature requires persisting provider metadata, add models
here following the standard pattern::

    from app.core.database import Base
    from sqlalchemy import Column, String
    from sqlalchemy.dialects.postgresql import UUID

    class ProviderConfig(Base):
        __tablename__ = "provider_configs"
        ...
"""

# No models defined — provider has no database tables.
# Import Base is available for future use:
# from app.core.database import Base
