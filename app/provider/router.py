"""Provider routes — gateway status, test LLM calls, and CRUD for provider configs."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import get_current_user_id, get_db, get_gateway
from app.core.schemas import PageResult, Result
from app.provider import schemas as provider_schemas
from app.provider import service as provider_service

settings = get_settings()
router = APIRouter(
    prefix="/provider",
    tags=["provider"],
)


class TestChatRequest(BaseModel):
    provider: str = Field(default="openai", description="Provider name: openai | anthropic")
    model: str = Field(default="", description="Model name, defaults to settings.DEFAULT_LLM_MODEL")
    message: str = Field(default="hi", description="Test message")


# ── Status ────────────────────────────────────────────────────────────────────


@router.get("/status")
async def provider_status(request: Request, _=Depends(get_current_user_id)):
    """Return registered providers and their API key status."""
    gw = request.app.state.gateway
    return Result.ok(
        {
            "llm_providers": gw.available_llm,
            "embedding_providers": gw.available_embedding,
        }
    ).model_dump()


@router.post("/test-chat")
async def provider_test_chat(
    body: TestChatRequest,
    gw=Depends(get_gateway),
    _=Depends(get_current_user_id),
):
    """Send a single test message and return the response (non-streaming)."""
    model = body.model or settings.default_llm_model
    response = await gw.chat(body.provider, model, [{"role": "user", "content": body.message}])
    return Result.ok({"response": response}).model_dump()


# ── Provider config CRUD ──────────────────────────────────────────────────────


@router.get("/configs")
async def list_configs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
) -> dict:
    """分页获取提供商配置列表。需登录。"""
    items, total = await provider_service.list_providers(db, page=page, page_size=page_size)
    data = [provider_service.provider_to_response(c) for c in items]
    return PageResult.ok(data, total=total, page=page, size=page_size).model_dump()


@router.post("/configs")
async def create_config(
    body: provider_schemas.ProviderConfigCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
) -> dict:
    """新增提供商配置。需登录。"""
    config = await provider_service.create_provider(
        db,
        name=body.name,
        provider_type=body.provider_type,
        base_url=body.base_url,
        auth_type=body.auth_type,
        auth_config=body.auth_config.model_dump() if body.auth_config else {},
        note=body.note,
    )
    return Result.ok(provider_service.provider_to_response(config)).model_dump()


@router.put("/configs/{config_id}")
async def update_config(
    config_id: uuid.UUID,
    body: provider_schemas.ProviderConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
) -> dict:
    """更新提供商配置。需登录。"""
    config = await provider_service.update_provider(
        db,
        config_id,
        name=body.name,
        provider_type=body.provider_type,
        base_url=body.base_url,
        auth_type=body.auth_type,
        auth_config=body.auth_config.model_dump() if body.auth_config else None,
        note=body.note,
        is_active=body.is_active,
    )
    return Result.ok(provider_service.provider_to_response(config)).model_dump()


@router.delete("/configs/{config_id}")
async def delete_config(
    config_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
) -> dict:
    """删除提供商配置（软删除）。需登录。"""
    await provider_service.delete_provider(db, config_id)
    return Result.ok(None).model_dump()


@router.post("/configs/{config_id}/test")
async def test_config(
    config_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
) -> dict:
    """测试指定提供商配置的连接。需登录。"""
    config = await provider_service.get_provider(db, config_id)
    auth_config = provider_service._decrypt_auth_config(config.auth_config)
    api_key = auth_config.get("api_key", "")

    test_message = "hello！现在是什么时间"
    try:
        # 为测试创建临时 provider 实例（不依赖启动时注册的 gateway）
        if config.provider_type == "openai":
            from app.provider.openai_provider import OpenAIProvider
            provider = OpenAIProvider(api_key=api_key, base_url=config.base_url or None)
        elif config.provider_type == "anthropic":
            from app.provider.anthropic_provider import AnthropicProvider
            provider = AnthropicProvider(api_key=api_key, base_url=config.base_url or None)
        else:
            return Result.ok({
                "ok": False,
                "provider": config.name,
                "error": f"不支持的提供商类型: {config.provider_type}",
            }).model_dump()

        response = await provider.chat(
            settings.default_llm_model,
            [{"role": "user", "content": test_message}],
        )

        # 测试通过 → 更新调用时间 + 健康状态 + 自动激活
        config.last_called_at = datetime.now(timezone.utc)
        await db.flush()

        await provider_service.update_health_status(db, config_id, success=True)

        if not config.is_active:
            config.is_active = True
            await db.flush()
        await db.refresh(config)

        return Result.ok({
            "ok": True,
            "provider": config.name,
            "model": settings.default_llm_model,
            "sent": test_message,
            "response": response,
        }).model_dump()
    except Exception as e:
        # 测试失败 → 更新健康状态
        await provider_service.update_health_status(
            db, config_id, success=False, error_message=str(e)
        )
        await db.refresh(config)
        return Result.ok({
            "ok": False,
            "provider": config.name,
            "error": str(e),
        }).model_dump()


# ── Provider model CRUD ─────────────────────────────────────────────────────


@router.get("/configs/{config_id}/models")
async def list_models(
    config_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
) -> dict:
    """获取指定供应商的所有模型。需登录。"""
    models = await provider_service.list_models(db, config_id)
    data = [provider_service.model_to_response(m) for m in models]
    return Result.ok(data).model_dump()


@router.post("/configs/{config_id}/models")
async def create_model(
    config_id: uuid.UUID,
    body: provider_schemas.ProviderModelCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
) -> dict:
    """为指定供应商新增模型。需登录。"""
    model = await provider_service.create_model(
        db,
        provider_config_id=config_id,
        model_name=body.model_name,
        display_name=body.display_name,
        supports_chat=body.supports_chat,
        supports_embedding=body.supports_embedding,
        supports_vision=body.supports_vision,
        max_tokens=body.max_tokens,
        default_temperature=body.default_temperature,
        input_cost_per_1k=body.input_cost_per_1k,
        output_cost_per_1k=body.output_cost_per_1k,
        is_enabled=body.is_enabled,
        sort_order=body.sort_order,
    )
    return Result.ok(provider_service.model_to_response(model)).model_dump()


@router.put("/configs/{config_id}/models/{model_id}")
async def update_model(
    config_id: uuid.UUID,
    model_id: uuid.UUID,
    body: provider_schemas.ProviderModelUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
) -> dict:
    """更新指定模型配置。需登录。"""
    model = await provider_service.update_model(
        db,
        model_id,
        **body.model_dump(exclude_none=True),
    )
    return Result.ok(provider_service.model_to_response(model)).model_dump()


@router.delete("/configs/{config_id}/models/{model_id}")
async def delete_model(
    config_id: uuid.UUID,
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
) -> dict:
    """删除指定模型配置。需登录。"""
    await provider_service.delete_model(db, model_id)
    return Result.ok(None).model_dump()


@router.get("/configs/models/batch")
async def batch_list_models(
    provider_ids: str = Query(..., description="逗号分隔的 provider UUID 列表"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
) -> dict:
    """批量获取多个供应商的模型列表，供前端列表页使用。需登录。"""
    ids = [uuid.UUID(pid.strip()) for pid in provider_ids.split(",") if pid.strip()]
    grouped = await provider_service.list_models_by_provider_ids(db, ids)
    data = {
        str(pid): [provider_service.model_to_response(m) for m in models]
        for pid, models in grouped.items()
    }
    return Result.ok(data).model_dump()


# ── Health check ──────────────────────────────────────────────────────────────


@router.post("/configs/{config_id}/health-check")
async def health_check_config(
    config_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
) -> dict:
    """手动触发供应商健康检测（轻量 ping）。需登录。"""
    config = await provider_service.get_provider(db, config_id)
    auth_config = provider_service._decrypt_auth_config(config.auth_config)
    api_key = auth_config.get("api_key", "")

    try:
        if config.provider_type == "openai":
            from app.provider.openai_provider import OpenAIProvider
            provider = OpenAIProvider(api_key=api_key, base_url=config.base_url or None)
        elif config.provider_type == "anthropic":
            from app.provider.anthropic_provider import AnthropicProvider
            provider = AnthropicProvider(api_key=api_key, base_url=config.base_url or None)
        else:
            return Result.ok({
                "ok": False,
                "health_status": config.health_status,
                "error": f"不支持的提供商类型: {config.provider_type}",
            }).model_dump()

        await provider.chat(
            settings.default_llm_model,
            [{"role": "user", "content": "ping"}],
        )

        await provider_service.update_health_status(db, config_id, success=True)
        await db.refresh(config)

        return Result.ok({
            "ok": True,
            "health_status": config.health_status,
            "last_health_check_at": config.last_health_check_at.isoformat() if config.last_health_check_at else None,
        }).model_dump()
    except Exception as e:
        await provider_service.update_health_status(
            db, config_id, success=False, error_message=str(e)
        )
        await db.refresh(config)
        return Result.ok({
            "ok": False,
            "health_status": config.health_status,
            "error": str(e),
        }).model_dump()
