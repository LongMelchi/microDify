# workflow/models.py
# SQLAlchemy ORM models for the workflow module.
# Only Column / relationship / ForeignKey / __tablename__ — no business methods.
# Max 100 lines; split into sub-module when exceeded.
#
# Tables:
#   workflows          — 工作流定义
#   workflow_nodes     — 工作流节点（类型、配置 JSON）
#   workflow_edges     — 节点间连线（源、目标、条件表达式）
#   workflow_executions — 工作流执行记录
# References: users (owner).

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Workflow(Base):
    """工作流定义"""

    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # relationships
    nodes = relationship("WorkflowNode", back_populates="workflow", cascade="all, delete-orphan")
    edges = relationship("WorkflowEdge", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowNode(Base):
    """工作流节点"""

    __tablename__ = "workflow_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # start, llm, knowledge_retrieval, condition, variable_transform, end
    label = Column(String(255), default="")
    config = Column(JSON, nullable=False, default=dict)  # type-specific configuration
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # relationships
    workflow = relationship("Workflow", back_populates="nodes")
    source_edges = relationship("WorkflowEdge", foreign_keys="WorkflowEdge.source_node_id", back_populates="source_node", cascade="all, delete-orphan")
    target_edges = relationship("WorkflowEdge", foreign_keys="WorkflowEdge.target_node_id", back_populates="target_node", cascade="all, delete-orphan")


class WorkflowEdge(Base):
    """节点间连线"""

    __tablename__ = "workflow_edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False, index=True)
    source_node_id = Column(UUID(as_uuid=True), ForeignKey("workflow_nodes.id"), nullable=False)
    target_node_id = Column(UUID(as_uuid=True), ForeignKey("workflow_nodes.id"), nullable=False)
    condition_expression = Column(Text, default="")  # empty for unconditional edges
    label = Column(String(255), default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # relationships
    workflow = relationship("Workflow", back_populates="edges")
    source_node = relationship("WorkflowNode", foreign_keys=[source_node_id], back_populates="source_edges")
    target_node = relationship("WorkflowNode", foreign_keys=[target_node_id], back_populates="target_edges")


class WorkflowExecution(Base):
    """工作流执行记录"""

    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending")  # pending, running, completed, failed, cancelled
    input_data = Column(JSON, nullable=False, default=dict)
    output_data = Column(JSON, nullable=True, default=None)
    node_results = Column(JSON, nullable=True, default=None)  # per-node execution results
    error_message = Column(Text, nullable=True, default=None)
    started_at = Column(DateTime(timezone=True), nullable=True, default=None)
    finished_at = Column(DateTime(timezone=True), nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # relationships
    workflow = relationship("Workflow", back_populates="executions")
