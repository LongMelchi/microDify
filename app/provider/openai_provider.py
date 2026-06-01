"""OpenAI provider — chat (streaming) + embeddings via the OpenAI SDK."""

from collections.abc import AsyncGenerator

import openai

from app.core.config import get_settings
from app.provider.base import BaseEmbeddingProvider, BaseLLMProvider

settings = get_settings()


class OpenAIProvider(BaseLLMProvider, BaseEmbeddingProvider):
    """LLM + Embedding adapter for the OpenAI API."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        super().__init__(api_key=api_key or settings.openai_api_key, base_url=base_url)
        self._client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=60.0,
        )

    # ── LLM ────────────────────────────────────────────────────────────────

    async def _chat_impl(self, model: str, messages: list[dict], **kwargs) -> str:
        model = model or settings.default_llm_model
        response = await self._client.chat.completions.create(
            model=model, messages=messages, **kwargs
        )
        return response.choices[0].message.content or ""

    async def _chat_stream_impl(
        self, model: str, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        model = model or settings.default_llm_model
        stream = await self._client.chat.completions.create(
            model=model, messages=messages, stream=True, **kwargs
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content

    # ── Embedding ──────────────────────────────────────────────────────────

    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        model = model or settings.default_embedding_model
        response = await self._client.embeddings.create(input=texts, model=model)
        return [d.embedding for d in response.data]
