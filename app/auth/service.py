"""认证业务逻辑

公开函数（通过 __init__.py 导出）:
    authenticate — 验证邮箱密码，返回 JWT
    create_user  — 注册新用户

依赖白名单: core/
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession


async def authenticate(
    db: AsyncSession,
    email: str,
    password: str,
) -> str | None:
    """验证用户凭证并返回 JWT token。

    Args:
        db: 数据库会话。
        email: 用户邮箱。
        password: 明文密码。

    Returns:
        JWT 字符串，验证失败返回 None。
    """
    # TODO: 查询 User → 校验 hashed_password → 签发 JWT
    ...


async def create_user(
    db: AsyncSession,
    email: str,
    username: str,
    password: str,
) -> uuid.UUID:
    """创建新用户。

    Args:
        db: 数据库会话。
        email: 用户邮箱。
        username: 用户名。
        password: 明文密码（内部哈希后存储）。

    Returns:
        新创建用户的 UUID。
    """
    # TODO: 校验唯一性 → 哈希密码 → 写入 User → 返回 id
    ...
