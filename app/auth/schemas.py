"""Pydantic 请求/响应模型

命名约定（CLAUDE.md §3）:
    XxxCreate   — 创建请求体
    XxxResponse — 响应体
    XxxFilter   — 查询过滤参数
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ─── Create ────────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    """创建用户请求"""

    email: EmailStr
    username: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)


# ─── Response ──────────────────────────────────────────────────────────


class UserResponse(BaseModel):
    """用户响应（不返回密码哈希）"""

    id: uuid.UUID
    email: str
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token 响应"""

    access_token: str
    token_type: str = "bearer"


# ─── Filter ────────────────────────────────────────────────────────────


class UserFilter(BaseModel):
    """用户列表过滤参数"""

    email: str | None = None
    username: str | None = None
