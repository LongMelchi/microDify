"""认证业务逻辑

公开函数（通过 __init__.py 导出）:
    authenticate — 验证邮箱密码，返回 JWT
    create_user  — 注册新用户
    get_user     — 按 ID 获取用户（返回 ORM 对象）

依赖白名单: core/
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.exceptions import BizException, ErrorCode
from app.core.security import create_token, verify_password


async def get_user(db: AsyncSession, user_id: uuid.UUID) -> User:
    """按 ID 获取用户，不存在则抛 BizException。"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise BizException(ErrorCode.NOT_FOUND, detail="用户不存在")
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """按邮箱查找用户（大小写不敏感），不存在返回 None。"""
    result = await db.execute(select(User).where(func.lower(User.email) == email.lower()))
    return result.scalar_one_or_none()


async def authenticate(
    db: AsyncSession,
    email: str,
    password: str,
) -> str:
    """验证用户凭证并返回 JWT token。

    Raises:
        BizException(UNAUTHORIZED): 邮箱或密码错误。
    """
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise BizException(ErrorCode.UNAUTHORIZED, detail="邮箱或密码错误")
    return create_token(str(user.id))


async def create_user(
    db: AsyncSession,
    email: str,
    username: str,
    password: str,
) -> uuid.UUID:
    """创建新用户。

    Raises:
        BizException(BAD_REQUEST): 邮箱或用户名已存在。
    """
    from app.core.security import hash_password

    # Check email uniqueness (case-insensitive)
    existing = await db.execute(
        select(User).where(func.lower(User.email) == email.lower())
    )
    if existing.scalar_one_or_none():
        raise BizException(ErrorCode.BAD_REQUEST, detail="邮箱已存在")

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
    )
    db.add(user)
    await db.flush()
    return user.id
