"""Anthropic provider — implements chat (streaming)."""

from collections.abc import AsyncGenerator

from app.provider.base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """LLM adapter for the Anthropic API (chat only, no embeddings)."""

    async def chat(self, model: str, messages: list[dict], **kwargs) -> str:
        raise NotImplementedError

    async def chat_stream(
        self, model: str, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        raise NotImplementedError
