"""Auth-specific FastAPI dependencies.

Lives in ``auth/`` (not ``core/``) because resolving the full ``User`` ORM
object requires importing ``app.auth.models`` — and ``core/`` must not depend
on any business module (CLAUDE.md dependency whitelist: ``core/`` imports = none).

``core.deps`` still owns the token-only dependency ``get_current_user_id``
(returns a ``UUID``, no business import).

Usage::

    from app.auth.deps import get_current_user
"""

import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user_id, get_db
from app.core.exceptions import BizException, ErrorCode


async def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Return the full ``User`` ORM object for the current request.

    Chains ``get_current_user_id`` (token decode) and ``get_db``.  Raises
    ``401`` via :class:`BizException` if the user no longer exists.
    """
    from app.auth.models import User

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise BizException(ErrorCode.UNAUTHORIZED, detail="用户不存在")
    return user
