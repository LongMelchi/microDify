"""Pydantic request/response schemas for the common module.

Naming convention (see CLAUDE.md §3):

    XxxCreate   — request body for POST /<resource>/
    XxxResponse — response body for GET/PATCH /<resource>/<id>
    XxxFilter   — query-string filters for GET /<resource>/
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ─── Response ──────────────────────────────────────────────────────────


class FileUploadResponse(BaseModel):
    """Response returned after a file is saved."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="File record UUID")
    filename: str = Field(..., description="Original file name")
    size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")
    url: str = Field(..., description="Access URL to the stored file")
    created_at: datetime = Field(..., description="Upload timestamp (UTC)")


class TaskResponse(BaseModel):
    """Response returned after a task is enqueued."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Task UUID")
    task_type: str = Field(..., description="Type of task (e.g. doc_parse, embed)")
    status: str = Field(..., description="Current status (pending / running / done / failed)")
    created_at: datetime = Field(..., description="Enqueue timestamp (UTC)")


class RateLimitResponse(BaseModel):
    """Response indicating current rate-limit status."""

    allowed: bool = Field(..., description="Whether the request is within the limit")
    remaining: int = Field(..., description="Requests remaining in the current window")
    reset_at: datetime = Field(..., description="When the rate-limit window resets (UTC)")


# ─── Filter ────────────────────────────────────────────────────────────


class TaskFilter(BaseModel):
    """Filter parameters for listing tasks."""

    model_config = ConfigDict(from_attributes=True)

    status: str | None = Field(default=None, description="Filter by task status")
    task_type: str | None = Field(default=None, description="Filter by task type")
