"""用户数据模型

表名: users
归属模块: auth/
"""

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampsMixin


class User(Base, TimestampsMixin):
    """平台用户，所有资源的归属点

    时间戳（created_at / updated_at）由 ``TimestampsMixin`` 统一提供。
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="developer"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )
