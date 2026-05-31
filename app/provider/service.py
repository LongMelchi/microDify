"""Provider service: unified LLM gateway.

Public class:
    LLMGateway — unified async interface for LLM chat completions and embeddings.

Design (CLAUDE.md §5):
    - async/await with ``httpx.AsyncClient`` singleton per provider
    - ``asyncio.Semaphore(10)`` limits concurrent LLM requests
    - 5-layer timeout: connect 10s, read 60s, first-token 30s, idle 15s, total 120s
    - Retry: max 3, exponential backoff (1s -> 2-4s jitter -> 4-8s jitter)
      on 429/5xx/ConnectionError/TimeoutError
    - L1 retry -> L2 provider failover -> L3 friendly error message

Dependency whitelist: core/

Concrete provider implementations (``OpenAIProvider``, ``AnthropicProvider``)
live in ``openai_provider.py`` and ``anthropic_provider.py`` respectively,
and are registered in ``registry.py``.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from typing import Any, Protocol


# ─── Type protocols ─────────────────────────────────────────────────────


class LLMProvider(Protocol):
    """Protocol that every LLM provider adapter must implement."""

    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float | None = 0.7,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Non-streaming chat completion. Returns {"content": str, "usage": {...}, ...}."""
        ...

    async def chat_completion_stream(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float | None = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Streaming chat completion. Yields delta chunks."""
        ...  # pragma: no cover
        yield  # make the generator syntactically valid

    async def embedding(
        self,
        model: str,
        input: str | list[str],
    ) -> dict[str, Any]:
        """Text embedding. Returns {"embeddings": list[list[float]], "usage": {...}}."""
        ...


# ─── LLMGateway ─────────────────────────────────────────────────────────


class LLMGateway:
    """Unified async gateway for LLM calls across all configured providers.

    Usage::

        gateway = LLMGateway()
        result = await gateway.chat_completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}],
        )

    Concurrency is capped at 10 simultaneous outbound LLM requests
    via ``asyncio.Semaphore``.  Each provider adapter manages its own
    ``httpx.AsyncClient`` connection pool.
    """

    def __init__(self) -> None:
        """Initialize the gateway.

        Provider adapters are loaded lazily from the registry at first call.
        """
        self._semaphore: Any = None  # asyncio.Semaphore(10) — set on first use
        self._providers: dict[str, LLMProvider] = {}  # populated lazily

    # ── Lifecycle ────────────────────────────────────────────────────────

    async def startup(self) -> None:
        """Initialise provider adapters and the concurrency semaphore.

        Called once during application startup (``app.main.lifespan``).
        """
        import asyncio

        self._semaphore = asyncio.Semaphore(10)
        # TODO: populate self._providers from registry
        # from app.provider.registry import get_providers
        # self._providers = get_providers()

    async def shutdown(self) -> None:
        """Gracefully close all provider HTTP clients.

        Called once during application shutdown.
        """
        for provider in self._providers.values():
            if hasattr(provider, "aclose"):
                await provider.aclose()  # type: ignore[union-attr]
        self._providers.clear()

    # ── Chat completions ─────────────────────────────────────────────────

    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float | None = 0.7,
        max_tokens: int | None = None,
        user_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        """Non-streaming chat completion.

        Args:
            model: Model identifier (e.g. ``"gpt-4o"``, ``"claude-sonnet-4-20250514"``).
            messages: Conversation messages in OpenAI-format list.
            temperature: Sampling temperature (0.0 — 2.0).
            max_tokens: Maximum tokens in the response.
            user_id: Optional user UUID for rate-limit tracking.

        Returns:
            Normalised response dict with keys ``content``, ``usage``, ``model``.

        Raises:
            RuntimeError: All providers failed after retries and failover.
        """
        assert self._semaphore is not None, "call .startup() before using the gateway"

        async with self._semaphore:
            provider = self._resolve_provider(model)
            # TODO: apply retry wrapper + L1/L2/L3 degradation
            return await provider.chat_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    async def chat_completion_stream(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float | None = 0.7,
        max_tokens: int | None = None,
        user_id: uuid.UUID | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Streaming chat completion (SSE-friendly).

        Yields delta chunks from the underlying provider.  If the stream
        is interrupted after the first token has been sent, the already-
        generated content is returned along with an interruption marker.

        Args:
            model: Model identifier.
            messages: Conversation messages.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.
            user_id: Optional user UUID for rate-limit tracking.

        Yields:
            Delta dicts — each yields ``{"delta": str, "finish_reason": str | None}``.
        """
        assert self._semaphore is not None, "call .startup() before using the gateway"

        async with self._semaphore:
            provider = self._resolve_provider(model)
            # TODO: apply retry wrapper + timeout management
            async for chunk in provider.chat_completion_stream(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            ):
                yield chunk

    # ── Embeddings ───────────────────────────────────────────────────────

    async def embedding(
        self,
        model: str,
        input: str | list[str],
        user_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        """Generate embeddings for the given input text(s).

        Args:
            model: Embedding model identifier (e.g. ``"text-embedding-3-small"``).
            input: Single text string or list of texts.
            user_id: Optional user UUID for rate-limit tracking.

        Returns:
            Normalised response dict with keys ``embeddings``, ``usage``, ``model``.
        """
        assert self._semaphore is not None, "call .startup() before using the gateway"

        async with self._semaphore:
            provider = self._resolve_provider(model)
            # TODO: apply retry wrapper
            return await provider.embedding(
                model=model,
                input=input,
            )

    # ── Internal helpers ─────────────────────────────────────────────────

    def _resolve_provider(self, model: str) -> LLMProvider:
        """Select the provider adapter responsible for *model*.

        TODO: implement provider resolution logic:
          1. Look up model -> provider mapping in registry.
          2. Fall back to default provider.
          3. On failure, attempt L2 failover to backup provider.
        """
        # Placeholder: return the first registered provider.
        if not self._providers:
            raise RuntimeError(
                "No LLM providers are configured. "
                "Set API keys in environment variables and call .startup()."
            )
        # TODO: map model prefix -> provider (e.g. "gpt-" -> OpenAI, "claude-" -> Anthropic)
        return next(iter(self._providers.values()))
