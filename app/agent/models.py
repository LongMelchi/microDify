"""Agent module database models.

Tables:
- agents: Agent 配置（系统指令、模型选择、enabled_tools JSON、知识库绑定）
- agent_executions: Agent 执行记录（输入、输出、ReAct 步骤 JSON、状态）
- agent_knowledge_bases: agents ↔ knowledge_bases 多对多关联表

预定义工具不建表：启用的工具以名称数组存于 agents.enabled_tools (JSON)。

Only Column / relationship / ForeignKey / __tablename__ — no business methods.
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base, TimestampsMixin


class Agent(Base, TimestampsMixin):
    """Agent 配置：系统指令、模型选择、enabled_tools、知识库绑定。

    时间戳（created_at / updated_at）由 ``TimestampsMixin`` 统一提供。
    """

    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)
    model_provider = Column(String(64), nullable=False)
    model_name = Column(String(128), nullable=False)
    enabled_tools = Column(JSON, nullable=False, default=list)  # 启用的预定义工具名数组
    status = Column(String(32), nullable=False, default="active")
    prompt_template_id = Column(UUID(as_uuid=True), ForeignKey("prompt_templates.id"), nullable=True)

    # relationships
    executions = relationship("AgentExecution", back_populates="agent", cascade="all, delete-orphan")
    # M:N to KnowledgeBase is resolved via explicit join on agent_knowledge_bases table


class AgentExecution(Base, TimestampsMixin):
    """Agent 执行记录：输入、输出、ReAct 步骤、状态。

    时间戳（created_at / updated_at）由 ``TimestampsMixin`` 统一提供；
    started_at / finished_at 为执行记录专用时间列，单独声明。
    """

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

    # relationships
    agent = relationship("Agent", back_populates="executions")


class AgentKnowledgeBase(Base):
    """agents ↔ knowledge_bases 多对多关联表。"""

    __tablename__ = "agent_knowledge_bases"

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    knowledge_base_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), primary_key=True)
