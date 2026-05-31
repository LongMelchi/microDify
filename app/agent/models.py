"""Agent module database models.

Tables:
- agents: Agent 配置（系统指令、模型选择、工具开关、知识库绑定）
- agent_executions: Agent 执行记录（输入、输出、ReAct 步骤 JSON、状态）
- agent_knowledge_bases: agents ↔ knowledge_bases 多对多关联表
- agent_tools: agents ↔ tools 多对多关联表

Only Column / relationship / ForeignKey / __tablename__ — no business methods.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Agent(Base):
    """Agent 配置：系统指令、模型选择、工具开关、知识库绑定。"""

    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)
    model_provider = Column(String(64), nullable=False)
    model_name = Column(String(128), nullable=False)
    tools_enabled = Column(JSON, nullable=False, default=dict)
    status = Column(String(32), nullable=False, default="active")
    prompt_template_id = Column(UUID(as_uuid=True), ForeignKey("prompt_templates.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # relationships
    executions = relationship("AgentExecution", back_populates="agent", cascade="all, delete-orphan")
    knowledge_bases = relationship(
        "KnowledgeBase",
        secondary="agent_knowledge_bases",
        back_populates="agents",
    )


class AgentExecution(Base):
    """Agent 执行记录：输入、输出、ReAct 步骤、状态。"""

    __tablename__ = "agent_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=True)
    reasoning_steps = Column(JSON, nullable=True)
    status = Column(String(32), nullable=False, default="running")
    tokens_used = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # relationships
    agent = relationship("Agent", back_populates="executions")


class AgentKnowledgeBase(Base):
    """agents ↔ knowledge_bases 多对多关联表。"""

    __tablename__ = "agent_knowledge_bases"

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    knowledge_base_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), primary_key=True)


class AgentTool(Base):
    """agents ↔ tools 多对多关联表。

    tool_id 为工具标识字符串（由 provider/ 定义的工具名称）。
    当前无独立 tools 表，未来可扩展为 FK 引用。
    """

    __tablename__ = "agent_tools"

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    tool_id = Column(String(128), primary_key=True)
