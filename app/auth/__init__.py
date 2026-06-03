"""认证模块：JWT + 账号密码

Public exports:
    router — APIRouter registered under /auth
    authenticate — validate credentials and return JWT
    create_user — register a new user account
"""

from app.auth.router import router
from app.auth.service import (
    authenticate,
    create_user,
    delete_user,
    get_user,
    get_user_by_email,
    list_users,
    update_user,
)

__all__ = [
    "router",
    "authenticate",
    "create_user",
    "delete_user",
    "get_user",
    "get_user_by_email",
    "list_users",
    "update_user",
]
