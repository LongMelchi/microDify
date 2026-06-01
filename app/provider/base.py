"""Abstract interfaces and cross-cutting concerns for LLM / Embedding providers.

All provider adapters MUST implement ``BaseLLMProvider`` (and optionally
``BaseEmbeddingProvider``).  Retry, timeout, and concurrency control are injected
here so that adapters contain only protocol-translation logic.
"""

from __future__ import annotations

import asyncio
import random
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

import httpx
import structlog

logger = structlog.get_logger("microdify.provider")

# Global semaphore — caps concurrent LLM calls across all providers.
_semaphore = asyncio.Semaphore(10)


# ── Retry helpers ──────────────────────────────────────────────────────────────

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_RETRYABLE_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.TimeoutException,
    httpx.RemoteProtocolError,
    ConnectionError,
    TimeoutError,
)
_MAX_RETRIES = 3


def _backoff(attempt: int) -> float:
    """Exponential backoff with jitter: 1s → 2-4s → 4-8s."""
    base = 2 ** (attempt - 1)
    return base + random.uniform(0, base)


def _is_retryable(exc: Exception, status_code: int | None) -> bool:
    """Return ``True`` if the error should be retried."""
    if status_code is not None:
        return status_code in _RETRYABLE_STATUS
    return isinstance(exc, _RETRYABLE_EXCEPTIONS)


async def _safe_aclose(gen) -> None:
    """Best-effort close of an abandoned async generator (ignore errors)."""
    aclose = getattr(gen, "aclose", None)
    if aclose is None:
        return
    try:
        await aclose()
    except Exception:  # noqa: BLE001 — cleanup must never raise
        pass


# ── Abstract interfaces ───────────────────────────────────────────────────────


class BaseLLMProvider(ABC):
    """Abstract interface for an LLM chat-completion provider.

    Subclasses only implement ``_chat_impl`` / ``_chat_stream_impl``; the public
    methods ``chat`` / ``chat_stream`` are wrapped by this base class with retry,
    timeout, and semaphore control.
    """

    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        self.api_key = api_key
        self.base_url = base_url

    # ── Subclass interface ─────────────────────────────────────────────────

    @abstractmethod
    async def _chat_impl(self, model: str, messages: list[dict], **kwargs) -> str:
        ...

    @abstractmethod
    async def _chat_stream_impl(
        self, model: str, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        ...

    # ── Public API (with cross-cutting concerns) ───────────────────────────

    async def chat(self, model: str, messages: list[dict], **kwargs) -> str:
        """Non-streaming chat with retry + semaphore."""
        async with _semaphore:
            return await _retry(lambda: self._chat_impl(model, messages, **kwargs))

    async def chat_stream(
        self, model: str, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streaming chat with retry, timeout, idle detection, and semaphore."""
        async with _semaphore:
            stream = _StreamWrapper(self, model, messages, kwargs)
            async for token in stream:
                yield token


class BaseEmbeddingProvider(ABC):
    """Abstract interface for an embedding provider."""

    @abstractmethod
    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        """Return embedding vectors for *texts*."""
        ...


# ── Retry + streaming support ─────────────────────────────────────────────────


async def _retry(fn, max_retries: int = _MAX_RETRIES):
    """Call *fn* up to *max_retries* with exponential backoff."""
    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return await fn()
        except Exception as exc:
            last_exc = exc
            status = getattr(exc, "status_code", None)
            if not _is_retryable(exc, status) or attempt >= max_retries:
                raise
            delay = _backoff(attempt)
            logger.warning(
                "Provider call failed — retrying",
                attempt=attempt,
                delay=round(delay, 2),
                error=str(exc)[:200],
            )
            await asyncio.sleep(delay)
    raise last_exc  # type: ignore[misc]


class _StreamWrapper:
    """Wraps a streaming call with first-token timeout (30 s), idle timeout
    (15 s), total timeout (120 s), and retry-on-early-failure.

    If the stream has *not* yielded any token when an error occurs we silently
    retry.  If tokens have already been emitted the stream is terminated with an
    interruption sentinel.
    """

    FIRST_TOKEN_TIMEOUT = 30
    IDLE_TIMEOUT = 15
    TOTAL_TIMEOUT = 120

    def __init__(self, provider, model: str, messages: list[dict], kwargs: dict) -> None:
        self._provider = provider
        self._model = model
        self._messages = messages
        self._kwargs = kwargs

    async def __aiter__(self):
        started_at = time.monotonic()
        yielded_any = False
        attempt = 0

        while attempt < _MAX_RETRIES:
            attempt += 1
            gen = self._provider._chat_stream_impl(
                self._model, self._messages, **self._kwargs
            )
            interrupted: Exception | None = None
            try:
                iterator = gen.__aiter__()
                while True:
                    remaining_total = self.TOTAL_TIMEOUT - (time.monotonic() - started_at)
                    if remaining_total <= 0:
                        if yielded_any:
                            # Partial content already delivered — end gracefully.
                            yield "\n\n[生成超时，已返回已生成内容]"
                            return
                        raise asyncio.TimeoutError("Total timeout before first token")

                    # Wait for the next token, bounded so a dead/idle stream is
                    # detected even when no token ever arrives.
                    per_token = (
                        self.FIRST_TOKEN_TIMEOUT if not yielded_any else self.IDLE_TIMEOUT
                    )
                    try:
                        token = await asyncio.wait_for(
                            iterator.__anext__(), timeout=min(per_token, remaining_total)
                        )
                    except StopAsyncIteration:
                        return  # natural end of stream

                    yielded_any = True
                    yield token
            except Exception as exc:  # noqa: BLE001 — classified below
                interrupted = exc
            finally:
                await _safe_aclose(gen)

            # Only reached when the inner loop raised (no return).
            status = getattr(interrupted, "status_code", None)
            if not yielded_any and _is_retryable(interrupted, status) and attempt < _MAX_RETRIES:
                delay = _backoff(attempt)
                logger.warning(
                    "Stream failed before first token — retrying",
                    attempt=attempt,
                    delay=round(delay, 2),
                )
                await asyncio.sleep(delay)
                continue

            # Tokens already sent → surface an interruption marker, then re-raise.
            if yielded_any:
                yield "\n\n[生成中断，请重试]"
            raise interrupted
