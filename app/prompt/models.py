# prompt/models.py
# SQLAlchemy ORM models for the prompt module.
# Only Column / relationship / ForeignKey / __tablename__ — no business methods.
# Max 100 lines; split into sub-module when exceeded.
#
# Table: prompt_templates
# Stores reusable prompt templates with {{variable}} placeholders.
# References: users (owner), chat_apps (usage), agents (usage).

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    description = Column(String(500), default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # relationships (populated by other modules via FK)
    user = relationship("User", back_populates="prompt_templates")
