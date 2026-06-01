"""FastAPI dependency injection factories.

Usage::

    from app.core.deps import get_current_user, get_current_user_id, get_db
"""

import uuid

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import decode_token

settings = get_settings()

# Standard bearer scheme — enables Swagger UI's Authorize button.
_bearer_scheme = HTTPBearer(auto_error=False)

# Token-only / infra dependencies. The full ``User`` ORM dependency lives in
# ``app.auth.deps.get_current_user`` because resolving it needs the auth model,
# and ``core/`` must not import business modules.
__all__ = ["get_current_user_id", "get_db", "get_gateway"]


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> uuid.UUID:
    """Extract the user ID from the JWT in the Authorization header.

    Raises ``401`` if the token is missing or invalid.
    """
    from fastapi import HTTPException

    if credentials is None:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")

    try:
        payload = decode_token(credentials.credentials)
        return uuid.UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")


def get_gateway(request: Request):
    """Return the :class:`LLMGateway` singleton from application state.

    Usage::

        @router.get("/chat")
        async def chat(gw = Depends(get_gateway)):
            async for token in gw.chat_stream("openai", "gpt-4o", [... ]):
                ...
    """
    return request.app.state.gateway
