"""认证路由

仅声明路径/方法、注入 Depends、调 service。不包含 DB 查询或业务逻辑。
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
