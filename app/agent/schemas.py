"""Pydantic 请求/响应模型

命名约定（CLAUDE.md §3）:
    XxxCreate   — 创建请求体
    XxxResponse — 响应体
    XxxFilter   — 查询过滤参数
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ─── Agent ────────────────────────────────────────────────────────────────


class AgentCreate(BaseModel):
    """创建 Agent 请求"""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    system_prompt: str = Field(..., min_length=1)
    model_provider: str = Field(..., min_length=1, max_length=64)
    model_name: str = Field(..., min_length=1, max_length=128)
    tools_enabled: dict | None = None
    knowledge_base_ids: list[UUID] | None = None
    prompt_template_id: UUID | None = None

    model_config = {"from_attributes": True}


class AgentResponse(BaseModel):
    """Agent 响应"""

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    system_prompt: str
    model_provider: str
    model_name: str
    tools_enabled: dict
    status: str
    prompt_template_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentFilter(BaseModel):
    """Agent 列表过滤参数"""

    name: str | None = None
    status: str | None = None
    model_provider: str | None = None


# ─── Agent Execution ──────────────────────────────────────────────────────


class AgentExecutionCreate(BaseModel):
    """启动 Agent 执行请求"""

    agent_id: UUID
    input: str = Field(..., min_length=1)

    model_config = {"from_attributes": True}


class AgentExecutionResponse(BaseModel):
    """Agent 执行记录响应"""

    id: UUID
    agent_id: UUID
    user_id: UUID
    input: str
    output: str | None
    reasoning_steps: list | None
    status: str
    tokens_used: int | None
    started_at: datetime
    finished_at: datetime | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentExecutionFilter(BaseModel):
    """Agent 执行记录过滤参数"""

    agent_id: UUID | None = None
    status: str | None = None
