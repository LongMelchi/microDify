"""模型提供商配置业务逻辑"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BizException, ErrorCode
from app.core.security import decrypt_api_key, encrypt_api_key
from app.provider.models import ProviderConfig


async def create_provider(
    db: AsyncSession,
    name: str,
    provider_type: str,
    base_url: str,
    api_key: str,
    note: str | None = None,
) -> ProviderConfig:
    """创建新的提供商配置（API Key 自动加密）。"""
    config = ProviderConfig(
        name=name,
        provider_type=provider_type,
        base_url=base_url,
        api_key=encrypt_api_key(api_key),
        note=note,
        is_active=False,  # 默认不活跃，测试连接通过后手动启用
    )
    db.add(config)
    await db.flush()
    await db.refresh(config)
    return config


async def list_providers(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ProviderConfig], int]:
    """分页获取提供商列表（排除已软删除）。"""
    base = select(ProviderConfig).where(ProviderConfig.is_deleted == False)
    count_stmt = select(func.count(ProviderConfig.id)).where(
        ProviderConfig.is_deleted == False
    )

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    stmt = base.order_by(ProviderConfig.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def get_provider(db: AsyncSession, provider_id: uuid.UUID) -> ProviderConfig:
    """按 ID 获取提供商，不存在则抛异常。"""
    stmt = select(ProviderConfig).where(
        ProviderConfig.id == provider_id, ProviderConfig.is_deleted == False
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        raise BizException(ErrorCode.NOT_FOUND, detail="提供商配置不存在")
    return config


async def update_provider(
    db: AsyncSession,
    provider_id: uuid.UUID,
    name: str | None = None,
    provider_type: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    note: str | None = None,
    is_active: bool | None = None,
) -> ProviderConfig:
    """更新提供商配置（只更新传入字段，api_key 自动重新加密）。"""
    config = await get_provider(db, provider_id)
    if name is not None:
        config.name = name
    if provider_type is not None:
        config.provider_type = provider_type
    if base_url is not None:
        config.base_url = base_url
    if api_key is not None:
        config.api_key = encrypt_api_key(api_key)
    if note is not None:
        config.note = note
    if is_active is not None:
        config.is_active = is_active
    await db.flush()
    await db.refresh(config)
    return config


async def delete_provider(db: AsyncSession, provider_id: uuid.UUID) -> None:
    """软删除提供商配置。"""
    config = await get_provider(db, provider_id)
    config.is_deleted = True
    await db.flush()


async def get_active_providers(
    db: AsyncSession,
) -> list[ProviderConfig]:
    """获取所有活跃且未删除的提供商配置（启动时加载）。"""
    stmt = select(ProviderConfig).where(
        ProviderConfig.is_active == True,
        ProviderConfig.is_deleted == False,
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


def provider_to_response(config: ProviderConfig) -> dict:
    """将 ORM 对象转为响应 dict（API Key 完整返回，由前端控制脱敏显示）。"""
    return {
        "id": str(config.id),
        "name": config.name,
        "provider_type": config.provider_type,
        "base_url": config.base_url,
        "api_key": decrypt_api_key(config.api_key),  # 完整 key，前端控制显隐
        "note": config.note,
        "is_active": config.is_active,
        "last_called_at": config.last_called_at.isoformat() if config.last_called_at else None,
        "created_at": config.created_at.isoformat() if config.created_at else "",
        "updated_at": config.updated_at.isoformat() if config.updated_at else "",
    }
