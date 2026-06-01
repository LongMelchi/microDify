"""JWT token creation and verification.

Usage::

    from app.core.security import create_token, decode_token, hash_password, verify_password
"""

import hashlib

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import structlog

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger("microdify.security")

# bcrypt only hashes the first 72 bytes of the input.
_BCRYPT_MAX_BYTES = 72


def create_token(user_id: str) -> str:
    """Create a JWT for *user_id* with the configured expiry."""
    payload = {
        "sub": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT.  Raises ``jwt.PyJWTError`` on failure."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt (random per-password salt).

    Returns the bcrypt hash string (``$2b$...``) for storage.  Inputs longer
    than 72 bytes are truncated, matching bcrypt's own behaviour.
    """
    raw = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Compare *plain* against a stored *hashed* password.

    Supports bcrypt hashes (``$2...``).  Legacy unsalted SHA-256 hashes (from the
    earlier stub) are still accepted for backward compatibility so existing
    accounts keep working — re-hash them with bcrypt on the next password change.
    """
    if hashed.startswith("$2"):
        raw = plain.encode("utf-8")[:_BCRYPT_MAX_BYTES]
        try:
            return bcrypt.checkpw(raw, hashed.encode("utf-8"))
        except ValueError:
            return False

    # Legacy SHA-256 fallback (insecure — migrate on next password set).
    logger.warning("verifying legacy sha256 password hash — should be re-hashed with bcrypt")
    return hashlib.sha256(plain.encode()).hexdigest() == hashed
