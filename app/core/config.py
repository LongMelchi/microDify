"""Application configuration via pydantic-settings.

All configuration is loaded from environment variables, with sensible defaults
for local development.  Production overrides are set in docker-compose.yml or
a ``.env`` file placed at the project root.

Usage::

    from app.core.config import get_settings

    settings = get_settings()
    print(settings.database_url)
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Values are read from environment variables first, then from a ``.env``
    file at the project root if one exists.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Application ---
    app_name: str = "microDify"
    debug: bool = True
    port: int = 8000
    workers: int = 2
    cors_origins: list[str] = ["*"]  # Production: set explicit origins

    # --- Database ---
    database_url: str = (
        "postgresql+asyncpg://microdify:microdify@localhost:5432/microdify"
    )
    db_pool_size: int = 10
    db_max_overflow: int = 5

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- LLM Provider ---
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_llm_model: str = "gpt-4o"
    default_embedding_model: str = "text-embedding-3-small"

    # --- Security ---
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # --- File Uploads ---
    upload_dir: str = "data/uploads"
    max_upload_size_mb: int = 20

    # --- Rate Limiting ---
    rate_limit_per_minute: int = 60


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` singleton.

    The cached instance lives for the lifetime of the process.  Call this
    function instead of constructing ``Settings()`` directly so that all
    consumers share the same loaded configuration.
    """
    return Settings()
