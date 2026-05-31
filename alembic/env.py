"""Alembic environment configuration.

This module is invoked by Alembic whenever the ``alembic`` CLI is used.  It
imports all ORM models so that ``Base.metadata`` reflects every table, and
overrides the database URL from the application's canonical settings source
(``app.core.config``) at runtime.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Alembic Config object — provides access to ``alembic.ini`` values.
config = context.config

# Set up Python logging from the INI file section.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import all ORM models so they are registered on Base.metadata ────────
# Each business module's models.py is imported here (even if unused in this
# file) so that Alembic's autogenerate detects every table.
# NOTE: core/models.py is imported separately because CoreModel is abstract.

from app.core.database import Base  # noqa: F401 — target_metadata
from app.core.models import CoreModel  # noqa: F401 — registers abstract base

# NOTE: CoreModel itself does not produce a table, but importing it is
# required so that derived models function correctly at import time.
# If the Base.metadata is still empty after imports, review whether the
# module's models.py has been imported below.

import app.auth.models  # noqa: F401 — users
import app.prompt.models  # noqa: F401 — prompt_templates
import app.knowledge.models  # noqa: F401 — knowledge_bases, documents, chunks
import app.chat.models  # noqa: F401 — chat_apps, conversations, messages
import app.agent.models  # noqa: F401 — agents, agent_executions

# NOTE: rag/ and provider/ produce no independent tables (rag/ operates on
# the chunk embedding column; provider/ is env-var driven).

import app.workflow.models  # noqa: F401 — workflows, workflow_nodes,
#                                   workflow_edges, workflow_executions

# Human-readable note for future maintainers:
#   - common/  — no models (utility services)
#   - core/    — only abstract base (CoreModel in core/models.py)
#   - rag/     — operates on knowledge.chunks.embedding column
#   - provider/ — no models (config via env vars)

# ── Runtime override of the database URL ──────────────────────────────────
# Read the connection string from the application's canonical settings so
# that all code paths use a single source of truth.

from app.core.config import get_settings

alembic_settings = get_settings()
config.set_main_option("sqlalchemy.url", alembic_settings.database_url)

# ── Metadata target for autogenerate ──────────────────────────────────────

target_metadata = Base.metadata


# ── Migration context helpers ─────────────────────────────────────────────


def run_migrations_offline() -> None:
    """Generate SQL migration scripts without connecting to a database.

    This mode is useful for review or when the target database is not
    directly accessible from the developer's machine.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the live database and apply migrations."""
    # Build a sync URL from the async URL (sync engine is needed by Alembic)
    sync_url = alembic_settings.database_url.replace(
        "postgresql+asyncpg://", "postgresql://"
    ).replace(
        "postgresql+psycopg://", "postgresql://"
    )

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=sync_url,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
