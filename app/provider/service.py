"""模型提供商配置业务逻辑"""

import copy
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BizException, ErrorCode
from app.core.security import decrypt_api_key, encrypt_api_key
from app.provider.models import HealthStatus, ProviderConfig, ProviderModel

# ── 鉴权配置加解密 ──────────────────────────────────────────────────────────

_AUTH_SENSITIVE_FIELDS = {"api_key", "client_secret"}


def _encrypt_auth_config(auth_config: dict) -> dict:
    """深拷贝后加密敏感字段，返回可安全存入 DB 的 dict。"""
    result = copy.deepcopy(auth_config)
    for field in _AUTH_SENSITIVE_FIELDS:
        if field in result and result[field]:
            result[field] = encrypt_api_key(result[field])
    return result


def _decrypt_auth_config(auth_config: dict) -> dict:
    """深拷贝后解密敏感字段，返回可对外展示的 dict。"""
    result = copy.deepcopy(auth_config)
    for field in _AUTH_SENSITIVE_FIELDS:
        if field in result and result[field]:
            try:
                result[field] = decrypt_api_key(result[field])
            except Exception:
                pass  # 解密失败保留原值（如手动修改了 DB）
    return result


# ── CRUD ────────────────────────────────────────────────────────────────────


async def create_provider(
    db: AsyncSession,
    name: str,
    provider_type: str,
    base_url: str,
    auth_type: str = "bearer",
    auth_config: dict | None = None,
    note: str | None = None,
) -> ProviderConfig:
    """创建新的提供商配置（auth_config 敏感字段自动加密）。"""
    config = ProviderConfig(
        name=name,
        provider_type=provider_type,
        base_url=base_url,
        auth_type=auth_type,
        auth_config=_encrypt_auth_config(auth_config or {}),
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
    auth_type: str | None = None,
    auth_config: dict | None = None,
    note: str | None = None,
    is_active: bool | None = None,
) -> ProviderConfig:
    """更新提供商配置（只更新传入字段，auth_config 敏感字段自动重新加密）。"""
    config = await get_provider(db, provider_id)
    if name is not None:
        config.name = name
    if provider_type is not None:
        config.provider_type = provider_type
    if base_url is not None:
        config.base_url = base_url
    if auth_type is not None:
        config.auth_type = auth_type
    if auth_config is not None:
        config.auth_config = _encrypt_auth_config(auth_config)
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
    """将 ORM 对象转为响应 dict（auth_config 敏感字段已解密，由前端控制显隐）。"""
    return {
        "id": str(config.id),
        "name": config.name,
        "provider_type": config.provider_type,
        "base_url": config.base_url,
        "auth_type": config.auth_type,
        "auth_config": _decrypt_auth_config(config.auth_config),
        "note": config.note,
        "is_active": config.is_active,
        "last_called_at": config.last_called_at.isoformat() if config.last_called_at else None,
        "health_status": config.health_status or "unknown",
        "last_health_check_at": config.last_health_check_at.isoformat() if config.last_health_check_at else None,
        "consecutive_failures": config.consecutive_failures or 0,
        "last_error_message": config.last_error_message,
        "created_at": config.created_at.isoformat() if config.created_at else "",
        "updated_at": config.updated_at.isoformat() if config.updated_at else "",
    }


# ── Health status tracking ──────────────────────────────────────────────────


def _next_health_status(
    current: str,
    success: bool,
    consecutive_failures: int,
) -> tuple[str, int]:
    """根据检测结果计算新的健康状态和失败计数（纯函数，无副作用）。

    状态转换：
    - 成功 → HEALTHY，失败计数归零
    - 失败 + UNKNOWN → UNHEALTHY
    - 失败 + HEALTHY + 连续失败 < 3 → 保持 HEALTHY
    - 失败 + HEALTHY + 连续失败 >= 3 → DEGRADED
    - 失败 + DEGRADED → UNHEALTHY
    - 失败 + UNHEALTHY → 保持 UNHEALTHY
    """
    if success:
        return HealthStatus.HEALTHY.value, 0

    failures = consecutive_failures + 1
    if current == HealthStatus.UNKNOWN.value:
        return HealthStatus.UNHEALTHY.value, failures
    if current == HealthStatus.HEALTHY.value and failures >= 3:
        return HealthStatus.DEGRADED.value, failures
    if current == HealthStatus.DEGRADED.value:
        return HealthStatus.UNHEALTHY.value, failures
    return current, failures


async def update_health_status(
    db: AsyncSession,
    provider_id: uuid.UUID,
    success: bool,
    error_message: str | None = None,
) -> ProviderConfig:
    """更新供应商健康状态（由 test 连接或实际 LLM 调用失败时触发）。"""
    config = await get_provider(db, provider_id)

    new_status, new_failures = _next_health_status(
        config.health_status or "unknown",
        success,
        config.consecutive_failures or 0,
    )

    config.health_status = new_status
    config.consecutive_failures = new_failures
    config.last_health_check_at = datetime.now(timezone.utc)
    if error_message:
        config.last_error_message = error_message[:500]
    elif success:
        config.last_error_message = None

    await db.flush()
    await db.refresh(config)
    return config


# ── Model CRUD ──────────────────────────────────────────────────────────────


async def create_model(
    db: AsyncSession,
    provider_config_id: uuid.UUID,
    model_name: str,
    display_name: str | None = None,
    supports_chat: bool = True,
    supports_embedding: bool = False,
    supports_vision: bool = False,
    max_tokens: int | None = None,
    default_temperature: float | None = None,
    input_cost_per_1k: float | None = None,
    output_cost_per_1k: float | None = None,
    is_enabled: bool = True,
    sort_order: int = 0,
) -> ProviderModel:
    """为指定供应商新增一个模型配置。"""
    # 先确认供应商存在
    await get_provider(db, provider_config_id)

    # 检查重名
    existing = await db.execute(
        select(ProviderModel).where(
            ProviderModel.provider_config_id == provider_config_id,
            ProviderModel.model_name == model_name,
        )
    )
    if existing.scalar_one_or_none():
        raise BizException(ErrorCode.BAD_REQUEST, detail="该供应商下已存在同名模型")

    model = ProviderModel(
        provider_config_id=provider_config_id,
        model_name=model_name,
        display_name=display_name,
        supports_chat=supports_chat,
        supports_embedding=supports_embedding,
        supports_vision=supports_vision,
        max_tokens=max_tokens,
        default_temperature=default_temperature,
        input_cost_per_1k=input_cost_per_1k,
        output_cost_per_1k=output_cost_per_1k,
        is_enabled=is_enabled,
        sort_order=sort_order,
    )
    db.add(model)
    await db.flush()
    await db.refresh(model)
    return model


async def list_models(
    db: AsyncSession,
    provider_config_id: uuid.UUID,
) -> list[ProviderModel]:
    """获取指定供应商下的所有模型（按 sort_order + model_name 排序）。"""
    stmt = (
        select(ProviderModel)
        .where(ProviderModel.provider_config_id == provider_config_id)
        .order_by(ProviderModel.sort_order, ProviderModel.model_name)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_model(db: AsyncSession, model_id: uuid.UUID) -> ProviderModel:
    """按 ID 获取模型，不存在则抛异常。"""
    stmt = select(ProviderModel).where(ProviderModel.id == model_id)
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()
    if not model:
        raise BizException(ErrorCode.NOT_FOUND, detail="模型配置不存在")
    return model


async def update_model(
    db: AsyncSession,
    model_id: uuid.UUID,
    **fields,
) -> ProviderModel:
    """更新模型配置（只更新传入的非 None 字段）。"""
    model = await get_model(db, model_id)
    for key, value in fields.items():
        if value is not None and hasattr(model, key):
            setattr(model, key, value)
    await db.flush()
    await db.refresh(model)
    return model


async def delete_model(db: AsyncSession, model_id: uuid.UUID) -> None:
    """物理删除模型配置。"""
    model = await get_model(db, model_id)
    await db.delete(model)
    await db.flush()


async def list_models_by_provider_ids(
    db: AsyncSession,
    provider_ids: list[uuid.UUID],
) -> dict[uuid.UUID, list[ProviderModel]]:
    """批量获取多个供应商的模型列表，返回 {provider_id: [models]}。

    用于前端列表页一次请求拿到所有供应商的模型数据。
    """
    if not provider_ids:
        return {}
    stmt = (
        select(ProviderModel)
        .where(ProviderModel.provider_config_id.in_(provider_ids))
        .order_by(ProviderModel.provider_config_id, ProviderModel.sort_order, ProviderModel.model_name)
    )
    result = await db.execute(stmt)
    models = result.scalars().all()
    grouped: dict[uuid.UUID, list[ProviderModel]] = {}
    for m in models:
        grouped.setdefault(m.provider_config_id, []).append(m)
    return grouped


def model_to_response(model: ProviderModel) -> dict:
    """将 ProviderModel ORM 对象转为响应 dict。"""
    return {
        "id": str(model.id),
        "provider_config_id": str(model.provider_config_id),
        "model_name": model.model_name,
        "display_name": model.display_name,
        "supports_chat": model.supports_chat,
        "supports_embedding": model.supports_embedding,
        "supports_vision": model.supports_vision,
        "max_tokens": model.max_tokens,
        "default_temperature": model.default_temperature,
        "input_cost_per_1k": model.input_cost_per_1k,
        "output_cost_per_1k": model.output_cost_per_1k,
        "is_enabled": model.is_enabled,
        "sort_order": model.sort_order,
        "created_at": model.created_at.isoformat() if model.created_at else "",
        "updated_at": model.updated_at.isoformat() if model.updated_at else "",
    }
