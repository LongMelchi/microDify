"""Common module ORM models.

Per CLAUDE.md §4, ``common/`` is reusable infrastructure (file storage, Redis
queue, rate limiting, event bus) and intentionally produces **no database
tables**:

    - file storage  → filesystem / object storage (path returned to caller)
    - rate limiting → Redis ``INCR + EXPIRE`` (no audit table)
    - queue / event → Redis lists (transient, not persisted)

If a concrete business module needs to persist file/task metadata, define that
table in *that module's* ``models.py`` (e.g. ``knowledge/`` owns its document
rows), not here.
"""

# No models defined — common has no database tables.
# from app.core.database import Base  # available if a future shared table is justified
