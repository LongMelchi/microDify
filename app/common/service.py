"""Common service layer — reusable async utilities.

All functions are pure async stubs.  Signatures accept only standard
Python parameters (db session, user id, business values) and never
receive Request / Response / BackgroundTasks objects.
"""

from uuid import UUID

from app.common.redis_client import get_redis


async def save_file(
    *,
    user_id: UUID,
    filename: str,
    content: bytes,
    mime_type: str | None = None,
) -> dict:
    """Persist an uploaded file to storage and return metadata.

    Args:
        user_id:  UUID of the uploading user.
        filename: Original file name (may be sanitised).
        content:  Raw binary content of the file.
        mime_type: Optional MIME type hint.

    Returns:
        Dictionary with keys ``id``, ``filename``, ``size``,
        ``mime_type``, ``url``, and ``created_at``.
    """
    # Stub — implementation will write to local filesystem or S3-compatible
    # storage, insert a FileRecord row, and return the metadata dict.
    _ = user_id, filename, content, mime_type
    raise NotImplementedError("save_file is not yet implemented")


async def enqueue_task(
    *,
    user_id: UUID,
    task_type: str,
    payload: dict,
) -> dict:
    """Push an async task onto the Redis-backed work queue.

    Args:
        user_id:   UUID of the requesting user.
        task_type: Identifier for the task handler (e.g. ``"doc_parse"``,
                   ``"embed"``).
        payload:   Arbitrary JSON-serialisable data consumed by the handler.

    Returns:
        Dictionary with keys ``id``, ``task_type``, ``status``, and
        ``created_at``.
    """
    # Stub — implementation will LPUSH to a Redis list, optionally
    # persist a QueueTask record, and return the metadata dict.
    _ = user_id, task_type, payload
    raise NotImplementedError("enqueue_task is not yet implemented")


async def check_rate_limit(
    *,
    user_id: UUID,
    action: str,
    max_requests: int = 60,
    window_seconds: int = 60,
) -> bool:
    """Return ``True`` if *user_id* is within the rate limit for *action*.

    Thin orchestration over :meth:`RedisClient.check_rate_limit` (the single
    source of the ``INCR + EXPIRE`` rolling-window logic).  Fails **open**
    (returns ``True``) when Redis is unavailable so a Redis outage never blocks
    user requests.

    Args:
        user_id:        UUID of the requesting user.
        action:         Rate-limit scope (e.g. ``"llm:chat"``, ``"api:upload"``).
        max_requests:   Maximum allowed requests within the window.
        window_seconds: Time window in seconds.
    """
    redis = await get_redis()
    if redis is None:
        return True
    return await redis.check_rate_limit(
        str(user_id), action, max_requests, window_seconds
    )
