"""Abstract interfaces for LLM and Embedding providers.

All provider adapters MUST implement these base classes.  The ``LLMGateway``
aggregates registered providers and exposes a unified API to upper modules.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator


class BaseLLMProvider(ABC):
    """Abstract interface for an LLM chat-completion provider."""

    @abstractmethod
    async def chat(self, model: str, messages: list[dict], **kwargs) -> str:
        """Non-streaming chat completion."""
        ...

    @abstractmethod
    async def chat_stream(
        self, model: str, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streaming chat completion — yields tokens one at a time."""
        ...


class BaseEmbeddingProvider(ABC):
    """Abstract interface for an embedding provider."""

    @abstractmethod
    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        """Return embedding vectors for *texts*."""
        ...
