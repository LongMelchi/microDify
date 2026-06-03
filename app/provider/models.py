"""模型提供商配置数据模型

表名: provider_configs
归属模块: provider/
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, SoftDeleteMixin, TimestampsMixin


class ProviderConfig(Base, TimestampsMixin, SoftDeleteMixin):
    """LLM 提供商配置 — API Key 经 Fernet 加密存储。

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
    api_key: Mapped[str] = mapped_column(String(500), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 默认未激活 — 由 service 在「测试连接」通过后才置为 True。
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    last_called_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
