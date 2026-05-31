"""Provider Pydantic schemas.

Naming convention (CLAUDE.md §3):

    XxxCreate   — request body for POST /<resource>/
    XxxResponse — response body for GET/PATCH /<resource>/<id>
    XxxFilter   — query-string filters for GET /<resource>/

Note: Most provider configuration is managed through environment variables
rather than REST API endpoints.  These schemas exist primarily for optional
admin/management endpoints and for the unified chat/embedding request path.
"""

from uuid import UUID

from pydantic import BaseModel, Field


# ─── Provider config ────────────────────────────────────────────────────


class ProviderCreate(BaseModel):
    """Create a provider override (e.g. custom endpoint, model alias)."""

    name: str = Field(..., min_length=1, max_length=100, description="Provider name")
    api_key: str = Field(..., min_length=1, description="API key for the provider")
    base_url: str | None = Field(None, description="Custom base URL")
    model: str = Field("gpt-4o", description="Default model identifier")


class ProviderResponse(BaseModel):
    """Provider configuration response (api_key is never returned)."""

    id: UUID
    name: str
    base_url: str | None = None
    model: str

    model_config = {"from_attributes": True}


class ProviderFilter(BaseModel):
    """Provider list query filters."""

    name: str | None = Field(None, max_length=100)
    model: str | None = Field(None, max_length=100)
