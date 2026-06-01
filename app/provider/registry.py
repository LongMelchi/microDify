"""Provider registry and unified LLM gateway.

Usage in ``main.py``::

    registry = ProviderRegistry()
    registry.register_llm("openai", OpenAIProvider(...))
    registry.register_llm("anthropic", AnthropicProvider(...))
    registry.register_embedding("openai", openai_provider)  # same instance
    gateway = LLMGateway(registry)
    app.state.gateway = gateway
"""

from collections.abc import AsyncGenerator

import structlog

from app.provider.base import BaseEmbeddingProvider, BaseLLMProvider

logger = structlog.get_logger("microdify.provider")


class ProviderRegistry:
    """Holds named :class:`BaseLLMProvider` / :class:`BaseEmbeddingProvider` instances."""

    def __init__(self) -> None:
        self._llm: dict[str, BaseLLMProvider] = {}
        self._embedding: dict[str, BaseEmbeddingProvider] = {}

    def register_llm(self, name: str, provider: BaseLLMProvider) -> None:
        self._llm[name] = provider

    def register_embedding(self, name: str, provider: BaseEmbeddingProvider) -> None:
        self._embedding[name] = provider

    def get_llm(self, name: str) -> BaseLLMProvider:
        if name not in self._llm:
            raise ValueError(f"LLM provider '{name}' is not registered. Available: {list(self._llm)}")
        return self._llm[name]

    def get_embedding(self, name: str) -> BaseEmbeddingProvider:
        if name not in self._embedding:
            raise ValueError(f"Embedding provider '{name}' is not registered. Available: {list(self._embedding)}")
        return self._embedding[name]

    def list_llm(self) -> list[str]:
        return list(self._llm)

    def list_embedding(self) -> list[str]:
        return list(self._embedding)


class LLMGateway:
    """Unified entry point for LLM and embedding operations.

    Modules (agent / chat / workflow) depend on the gateway, not on individual
    adapters, so adding a new provider only touches ``main.py`` startup.

    Degradation chain (CLAUDE.md §5): L1 retry + 5-layer timeout live in the
    adapter base class; this gateway adds **L2 provider failover** (try the
    requested provider, then any other registered provider); L3 (friendly error)
    is the global ``LLM_ERROR`` handler when every provider is exhausted.

    Note: failover passes the caller's ``model`` through unchanged. Cross-provider
    model aliasing (e.g. mapping a gpt-* request onto a claude-* model) is a
    deliberate follow-up and not handled here.
    """

    def __init__(self, registry: ProviderRegistry) -> None:
        self._registry = registry

    def _failover_order(self, provider_name: str) -> list[str]:
        """Return the requested provider first, then the rest, as a fallback chain."""
        available = self._registry.list_llm()
        ordered = [provider_name] + [n for n in available if n != provider_name]
        return [n for n in ordered if n in available]

    async def chat_stream(
        self, provider_name: str, model: str, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        candidates = self._failover_order(provider_name)
        for index, name in enumerate(candidates):
            yielded_any = False
            try:
                async for token in self._registry.get_llm(name).chat_stream(
                    model, messages, **kwargs
                ):
                    yielded_any = True
                    yield token
                return
            except Exception as exc:
                # Can only fail over before any token reached the client.
                if yielded_any or index == len(candidates) - 1:
                    raise
                logger.warning(
                    "LLM stream provider failed before first token — failing over",
                    provider=name,
                    fallback=candidates[index + 1],
                    error=str(exc)[:200],
                )

    async def chat(self, provider_name: str, model: str, messages: list[dict], **kwargs) -> str:
        candidates = self._failover_order(provider_name)
        last_exc: Exception | None = None
        for name in candidates:
            try:
                return await self._registry.get_llm(name).chat(model, messages, **kwargs)
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "LLM provider failed — trying next",
                    provider=name,
                    error=str(exc)[:200],
                )
        raise last_exc  # type: ignore[misc]  # all providers exhausted → L3 handler

    async def embed(self, provider_name: str, texts: list[str], model: str | None = None):
        ep = self._registry.get_embedding(provider_name)
        return await ep.embed(texts, model)

    @property
    def available_llm(self) -> list[str]:
        return self._registry.list_llm()

    @property
    def available_embedding(self) -> list[str]:
        return self._registry.list_embedding()
