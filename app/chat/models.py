"""Chat module database models.

Tables:
- chat_apps: 对话应用，绑定 Prompt 模板 + 可选关联知识库
- conversations: 一次对话会话，归属一个对话应用
- messages: 会话中的一条消息，归属一个会话
- chat_app_knowledge_bases: chat_apps ↔ knowledge_bases 多对多关联表
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ChatApp(Base):
    """对话应用：绑定 Prompt 模板，可选关联知识库。"""

    __tablename__ = "chat_apps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    prompt_template_id = Column(UUID(as_uuid=True), ForeignKey("prompt_templates.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # relationships
    conversations = relationship("Conversation", back_populates="chat_app", cascade="all, delete-orphan")
    knowledge_bases = relationship(
        "KnowledgeBase",
        secondary="chat_app_knowledge_bases",
        back_populates="chat_apps",
    )


class Conversation(Base):
    """一次对话会话，归属一个对话应用。"""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=True)
    chat_app_id = Column(UUID(as_uuid=True), ForeignKey("chat_apps.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # relationships
    chat_app = relationship("ChatApp", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    """会话中的一条消息，归属一个会话。"""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(32), nullable=False)  # user / assistant / system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # relationships
    conversation = relationship("Conversation", back_populates="messages")


class ChatAppKnowledgeBase(Base):
    """chat_apps ↔ knowledge_bases 多对多关联表。"""

    __tablename__ = "chat_app_knowledge_bases"

    chat_app_id = Column(UUID(as_uuid=True), ForeignKey("chat_apps.id", ondelete="CASCADE"), primary_key=True)
    knowledge_base_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), primary_key=True)
