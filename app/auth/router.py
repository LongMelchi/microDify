"""认证路由

仅声明路径/方法、注入 Depends、调 service、包装 Result。不包含 DB 查询或业务逻辑。
"""

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import schemas, service
from app.auth.deps import get_current_user
from app.common.redis_client import RedisClient, get_redis
from app.core.deps import get_db
from app.core.exceptions import BizException, ErrorCode
from app.core.schemas import Result
from app.core.security import create_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

logger = structlog.get_logger("microdify.auth")


@router.post("/login")
async def login(
    body: schemas.LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis: RedisClient | None = Depends(get_redis),
) -> dict:
    """用户登录，返回 JWT token。失败 5 次/5 分钟触发限流。"""
    # Rate-limit failed logins
    if redis is not None:
        try:
            allowed = await redis.check_rate_limit(
                f"login_failed:{body.email}",
                "auth_login",
                max_count=5,
                window_seconds=300,
            )
            if not allowed:
                raise BizException(
                    ErrorCode.TOO_MANY_REQUESTS,
                    detail="登录失败次数过多，请 5 分钟后再试",
                )
        except BizException:
            raise
        except Exception:
            logger.warning("Redis unavailable, skipping rate limit", exc_info=True)
    else:
        logger.warning("Redis not configured, skipping rate limit")

    # Authenticate
    token_str = await service.authenticate(db, body.email, body.password)
    return Result.ok(
        schemas.TokenResponse(access_token=token_str).model_dump()
    ).model_dump()


@router.post("/register")
async def register(
    body: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
    redis: RedisClient | None = Depends(get_redis),
) -> dict:
    """注册新用户，成功后自动登录并返回 JWT token。

    一期不设注册限流（团队内部 20-50 人，注册频率极低）。
    """
    # 可选：未来可加 Redis IP 限流（3 次/小时），key = f"register:{request.client.host}"
    if redis is not None:
        logger.debug("Redis available for future registration rate limiting")

    user_id = await service.create_user(
        db,
        email=body.email,
        username=body.username,
        password=body.password,
    )
    token_str = create_token(str(user_id))
    logger.info("User registered", extra={"user_id": str(user_id), "email": body.email})
    return Result.ok(
        schemas.TokenResponse(access_token=token_str).model_dump()
    ).model_dump()


@router.get("/me")
async def get_current_user_info(
    user=Depends(get_current_user),
) -> dict:
    """获取当前登录用户信息（演示 ORM → Pydantic → Result 转换链）"""
    return Result.ok(
        schemas.UserResponse.model_validate(user).model_dump()
    ).model_dump()
