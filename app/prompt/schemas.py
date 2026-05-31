# prompt/schemas.py
# Pydantic schemas for the prompt module.
# Only BaseModel + Field — no DB queries, no service calls.
# Max 100 lines; split into schemas/ directory when exceeded.
#
# Naming convention (three suffixes):
#   XxxCreate  — request body for creation / update
#   XxxResponse — response body returned to client
#   XxxFilter  — query-string / filter parameters for listing

from datetime import datetime

from pydantic import BaseModel, Field


class PromptTemplateCreate(BaseModel):
    """Request schema for creating a new prompt template."""
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    content: str = Field(..., min_length=1, description="Template content with {{variable}} placeholders")
    description: str = Field("", max_length=500, description="Optional description")


class PromptTemplateResponse(BaseModel):
    """Response schema for a prompt template."""
    id: str = Field(..., description="UUID of the template")
    user_id: str = Field(..., description="UUID of the owner")
    name: str = Field(..., description="Template name")
    content: str = Field(..., description="Template content")
    description: str = Field("", description="Optional description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PromptTemplateFilter(BaseModel):
    """Filter / query parameters for listing prompt templates."""
    name: str | None = Field(None, max_length=255, description="Filter by name (partial match)")
