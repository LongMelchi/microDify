"""Provider service entrypoint.

The unified LLM gateway and provider registry live in ``registry.py``
(:class:`LLMGateway` / :class:`ProviderRegistry`), which wrap the retry /
timeout / streaming concerns implemented in ``base.py`` and the concrete
adapters in ``openai_provider.py`` / ``anthropic_provider.py``.

This module re-exports them so the provider module exposes a single,
canonical service surface — there is intentionally **no** second gateway
implementation here.

Design (CLAUDE.md §5):
    - async/await, ``httpx.AsyncClient`` singleton per provider
    - ``asyncio.Semaphore(10)`` caps concurrent LLM requests (see ``base.py``)
    - 5-layer timeout (connect / read / first-token / idle / total)
    - Retry: max 3, exponential backoff on 429 / 5xx / Connection / Timeout
    - Degradation: L1 retry -> L2 provider failover -> L3 friendly error
"""

from app.provider.registry import LLMGateway, ProviderRegistry

__all__ = ["LLMGateway", "ProviderRegistry"]
