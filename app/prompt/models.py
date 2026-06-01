# prompt/models.py
# SQLAlchemy ORM models for the prompt module.
# Only Column / relationship / ForeignKey / __tablename__ — no business methods.
# Max 100 lines; split into sub-module when exceeded.
#
# Table: prompt_templates
# Stores reusable prompt templates with {{variable}} placeholders.
# References: users (owner), chat_apps (usage), agents (usage).

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column

from app.core.database import Base, TimestampsMixin


class PromptTemplate(Base, TimestampsMixin):
    """Prompt 模板。

    时间戳（created_at / updated_at）由 ``TimestampsMixin`` 统一提供。
    """

    __tablename__ = "prompt_templates"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = mapped_column(String(255), nullable=False)
    content = mapped_column(Text, nullable=False)
    description = mapped_column(String(500), default="")
