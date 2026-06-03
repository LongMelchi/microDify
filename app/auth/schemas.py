"""Pydantic 请求/响应模型

命名约定（CLAUDE.md §3）:
    XxxCreate   — 创建请求体
    XxxResponse — 响应体，继承 CoreResponse
    XxxFilter   — 查询过滤参数
"""

import uuid

from pydantic import BaseModel, Field

from app.core.schemas import CoreResponse


# ─── Create ────────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    """创建用户请求"""

    email: str = Field(..., min_length=3, max_length=255)
    username: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """登录请求"""

    email: str = Field(..., min_length=3, max_length=255)
    password: str


# ─── Response ──────────────────────────────────────────────────────────


class UserResponse(CoreResponse):
    """用户响应（不返回密码哈希）"""

    email: str
    username: str
    role: str = "developer"
    status: str = "active"


class TokenResponse(BaseModel):
    """JWT token 响应"""

    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    """更新用户信息（所有字段可选，只更新传入的）"""

    username: str | None = Field(None, min_length=2, max_length=100)
    status: str | None = Field(None, pattern="^(active|inactive)$")


# ─── Filter ────────────────────────────────────────────────────────────


class UserFilter(BaseModel):
    """用户列表过滤参数"""

    email: str | None = None
    username: str | None = None
    role: str | None = None
    status: str | None = None
