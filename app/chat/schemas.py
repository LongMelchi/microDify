"""Chat module Pydantic schemas.

Naming convention:
  XxxCreate   - request body for creating a resource
  XxxResponse - response body returned to the client
  XxxFilter   - query parameters for listing/filtering
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ── ChatApp ────────────────────────────────────────────────────────────

class ChatAppCreate(BaseModel):
    """Request schema for creating a chat application."""
    name: str = Field(..., min_length=1, max_length=255, description="Chat app name")
    description: Optional[str] = Field(None, description="Optional description")
    prompt_template_id: Optional[UUID] = Field(None, description="Bound prompt template ID")
    knowledge_base_ids: Optional[list[UUID]] = Field(None, description="Linked knowledge base IDs")


class ChatAppResponse(BaseModel):
    """Response schema for a chat application."""
    id: UUID
    name: str
    description: Optional[str] = None
    prompt_template_id: Optional[UUID] = None
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatAppFilter(BaseModel):
    """Query filter for listing chat applications."""
    name: Optional[str] = Field(None, description="Partial name search")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


# ── Conversation ───────────────────────────────────────────────────────

class ConversationCreate(BaseModel):
    """Request schema for creating a conversation."""
    title: Optional[str] = Field(None, max_length=255, description="Conversation title")


class ConversationResponse(BaseModel):
    """Response schema for a conversation."""
    id: UUID
    title: Optional[str] = None
    chat_app_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationFilter(BaseModel):
    """Query filter for listing conversations."""
    chat_app_id: UUID = Field(..., description="Parent chat app ID")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


# ── Message ────────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    """Request schema for sending a message (user input)."""
    content: str = Field(..., min_length=1, description="User message content")


class MessageResponse(BaseModel):
    """Response schema for a message."""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageFilter(BaseModel):
    """Query filter for listing messages."""
    conversation_id: UUID = Field(..., description="Parent conversation ID")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=200, description="Items per page")
