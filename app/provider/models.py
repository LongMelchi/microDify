"""模型提供商配置数据模型

表名: provider_configs
归属模块: provider/
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, SoftDeleteMixin, TimestampsMixin


class AuthType(str, enum.Enum):
    """LLM 提供商鉴权方式枚举。

    各方式对应的 auth_config JSONB 结构::

        bearer / api_key_header → {"api_key": "<Fernet 密文>"}
        oauth_cc                → {"client_id": "xxx", "client_secret": "<密文>", "token_url": "https://..."}
        none                    → {}
    """

    BEARER = "bearer"
    API_KEY_HEADER = "api_key_header"
    OAUTH_CC = "oauth_cc"
    NONE = "none"


class HealthStatus(str, enum.Enum):
    """供应商健康状态枚举 — 由系统自动维护，非用户手动设置。"""

    UNKNOWN = "unknown"       # 从未检测过
    HEALTHY = "healthy"       # 最近一次检测成功
    DEGRADED = "degraded"     # 最近有失败，但仍能部分工作
    UNHEALTHY = "unhealthy"   # 最近一次检测失败，不可用


class ProviderConfig(Base, TimestampsMixin, SoftDeleteMixin):
    """LLM 提供商配置 — 鉴权信息经 Fernet 加密存入 ``auth_config`` JSONB。

    时间戳由 ``TimestampsMixin`` 提供，软删除由 ``SoftDeleteMixin`` 提供。
    """

    __tablename__ = "provider_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_type: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    # 鉴权方式 + 统一鉴权参数 JSONB（替代旧 api_key 列）。
    auth_type: Mapped[str] = mapped_column(
        String(20), default="bearer", nullable=False
    )
    auth_config: Mapped[dict] = mapped_column(
        JSONB, default=dict, nullable=False
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 默认未激活 — 由 service 在「测试连接」通过后才置为 True。
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    last_called_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    # ── 健康状态（系统自动维护） ─────────────────────────────────────────
    health_status: Mapped[str] = mapped_column(
        String(20), default="unknown", nullable=False, index=True
    )
    last_health_check_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    consecutive_failures: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    last_error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )


class ProviderModel(Base, TimestampsMixin):
    """供应商下的模型配置 — 归属于一个 ProviderConfig。

    时间戳由 ``TimestampsMixin`` 提供。
    注意：此表不需要软删除（模型直接物理删除）。
    """

    __tablename__ = "provider_models"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    provider_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("provider_configs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # 能力标记
    supports_chat: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    supports_embedding: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    supports_vision: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 参数约束（可选）
    max_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    default_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)

    # 成本追踪（可选，为后续用量统计预留）
    input_cost_per_1k: Mapped[float | None] = mapped_column(Float, nullable=True)
    output_cost_per_1k: Mapped[float | None] = mapped_column(Float, nullable=True)

    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 同一个供应商下模型名不可重复
    __table_args__ = (
        UniqueConstraint(
            "provider_config_id", "model_name",
            name="uq_provider_model",
        ),
    )
