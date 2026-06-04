"""Pydantic 请求/响应模型 for ProviderConfig"""

from pydantic import BaseModel, Field

from app.core.schemas import CoreResponse


# ── 鉴权配置子模型 ──────────────────────────────────────────────────────────

_AUTH_TYPE_PATTERN = "^(bearer|api_key_header|oauth_cc|none)$"


class AuthConfigSchema(BaseModel):
    """鉴权配置 — 对外接口使用，内部敏感字段由 service 层加解密。

    bearer / api_key_header → api_key
    oauth_cc                → client_id + client_secret + token_url
    none                    → 全部为空
    """

    api_key: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    token_url: str | None = None


# ── Provider Config 请求/响应 ───────────────────────────────────────────────


class ProviderConfigCreate(BaseModel):
    """创建提供商配置"""

    name: str = Field(..., min_length=1, max_length=100)
    provider_type: str = Field(..., pattern="^(openai|anthropic)$")
    base_url: str = Field(..., min_length=1, max_length=500)
    auth_type: str = Field(default="bearer", pattern=_AUTH_TYPE_PATTERN)
    auth_config: AuthConfigSchema = Field(default_factory=AuthConfigSchema)
    note: str | None = None


class ProviderConfigUpdate(BaseModel):
    """更新提供商配置（所有字段可选）"""

    name: str | None = Field(None, min_length=1, max_length=100)
    provider_type: str | None = Field(None, pattern="^(openai|anthropic)$")
    base_url: str | None = Field(None, min_length=1, max_length=500)
    auth_type: str | None = Field(None, pattern=_AUTH_TYPE_PATTERN)
    auth_config: AuthConfigSchema | None = None
    note: str | None = None
    is_active: bool | None = None


class ProviderConfigResponse(CoreResponse):
    """提供商配置响应 — auth_config 中敏感字段为解密后的完整值"""

    name: str
    provider_type: str
    base_url: str
    auth_type: str = "bearer"
    auth_config: AuthConfigSchema = Field(default_factory=AuthConfigSchema)
    note: str | None = None
    is_active: bool = True
    last_called_at: str | None = None
    health_status: str = "unknown"
    last_health_check_at: str | None = None
    consecutive_failures: int = 0
    last_error_message: str | None = None


# ── Provider Model 请求/响应 ─────────────────────────────────────────────────


class ProviderModelCreate(BaseModel):
    """创建供应商模型"""

    model_name: str = Field(..., min_length=1, max_length=100)
    display_name: str | None = None
    supports_chat: bool = True
    supports_embedding: bool = False
    supports_vision: bool = False
    max_tokens: int | None = Field(None, ge=1)
    default_temperature: float | None = Field(None, ge=0.0, le=2.0)
    input_cost_per_1k: float | None = Field(None, ge=0.0)
    output_cost_per_1k: float | None = Field(None, ge=0.0)
    is_enabled: bool = True
    sort_order: int = 0


class ProviderModelUpdate(BaseModel):
    """更新供应商模型（所有字段可选）"""

    model_name: str | None = Field(None, min_length=1, max_length=100)
    display_name: str | None = None
    supports_chat: bool | None = None
    supports_embedding: bool | None = None
    supports_vision: bool | None = None
    max_tokens: int | None = Field(None, ge=1)
    default_temperature: float | None = Field(None, ge=0.0, le=2.0)
    input_cost_per_1k: float | None = Field(None, ge=0.0)
    output_cost_per_1k: float | None = Field(None, ge=0.0)
    is_enabled: bool | None = None
    sort_order: int | None = None


class ProviderModelResponse(CoreResponse):
    """供应商模型响应"""

    id: str
    provider_config_id: str
    model_name: str
    display_name: str | None = None
    supports_chat: bool = True
    supports_embedding: bool = False
    supports_vision: bool = False
    max_tokens: int | None = None
    default_temperature: float | None = None
    input_cost_per_1k: float | None = None
    output_cost_per_1k: float | None = None
    is_enabled: bool = True
    sort_order: int = 0
    created_at: str = ""
