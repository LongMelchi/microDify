"""OpenAI provider — implements chat (streaming) + embeddings."""

from collections.abc import AsyncGenerator

from app.provider.base import BaseEmbeddingProvider, BaseLLMProvider


class OpenAIProvider(BaseLLMProvider, BaseEmbeddingProvider):
    """LLM + Embedding adapter for the OpenAI API."""

    async def chat(self, model: str, messages: list[dict], **kwargs) -> str:
        raise NotImplementedError

    async def chat_stream(
        self, model: str, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        raise NotImplementedError

    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        raise NotImplementedError
