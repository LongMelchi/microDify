"""Pydantic 请求/响应模型 for ProviderConfig"""

from pydantic import BaseModel, Field

from app.core.schemas import CoreResponse


class ProviderConfigCreate(BaseModel):
    """创建提供商配置"""

    name: str = Field(..., min_length=1, max_length=100)
    provider_type: str = Field(..., pattern="^(openai|anthropic)$")
    base_url: str = Field(..., min_length=1, max_length=500)
    api_key: str = Field(..., min_length=1, max_length=500)
    note: str | None = None


class ProviderConfigUpdate(BaseModel):
    """更新提供商配置（所有字段可选）"""

    name: str | None = Field(None, min_length=1, max_length=100)
    provider_type: str | None = Field(None, pattern="^(openai|anthropic)$")
    base_url: str | None = Field(None, min_length=1, max_length=500)
    api_key: str | None = Field(None, min_length=1, max_length=500)
    note: str | None = None
    is_active: bool | None = None


class ProviderConfigResponse(CoreResponse):
    """提供商配置响应"""

    name: str
    provider_type: str
    base_url: str
    api_key: str  # 脱敏显示
    note: str | None = None
    is_active: bool = True
    last_called_at: str | None = None
