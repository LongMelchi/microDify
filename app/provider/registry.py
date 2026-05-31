"""Provider registry — maps provider names to adapter instances.

Upper modules resolve providers via :class:`LLMGateway`, not directly from the
registry.
"""

from app.provider.base import BaseEmbeddingProvider, BaseLLMProvider


class LLMGateway:
    """Unified entry point for LLM and embedding operations.

    Wraps the :class:`ProviderRegistry` and delegates to the correct adapter
    based on *provider_name*.
    """

    def __init__(self, registry: "ProviderRegistry") -> None:
        self._registry = registry

    # -- to be implemented -----------------------------------------------------

    async def chat_stream(self, provider_name: str, model: str, messages: list[dict], **kwargs):
        raise NotImplementedError

    async def embed(self, provider_name: str, texts: list[str]):
        raise NotImplementedError


class ProviderRegistry:
    """Registry that holds named :class:`BaseLLMProvider` / :class:`BaseEmbeddingProvider` instances."""

    def register_llm(self, name: str, provider: BaseLLMProvider) -> None:
        raise NotImplementedError

    def register_embedding(self, name: str, provider: BaseEmbeddingProvider) -> None:
        raise NotImplementedError

    def get_llm(self, name: str) -> BaseLLMProvider:
        raise NotImplementedError

    def get_embedding(self, name: str) -> BaseEmbeddingProvider:
        raise NotImplementedError
