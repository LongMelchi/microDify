"""Anthropic provider — chat (streaming) via the Anthropic SDK."""

from collections.abc import AsyncGenerator

import anthropic

from app.core.config import get_settings
from app.provider.base import BaseLLMProvider

settings = get_settings()


class AnthropicProvider(BaseLLMProvider):
    """LLM adapter for the Anthropic API (chat only, no embeddings)."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        super().__init__(api_key=api_key or settings.anthropic_api_key, base_url=base_url)
        self._client = anthropic.AsyncAnthropic(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=60.0,
        )

    # ── LLM ────────────────────────────────────────────────────────────────

    async def _chat_impl(self, model: str, messages: list[dict], **kwargs) -> str:
        model = model or settings.default_llm_model
        system, chat_messages = _extract_system(messages)
        response = await self._client.messages.create(
            model=model,
            max_tokens=kwargs.pop("max_tokens", 4096),
            system=system,
            messages=chat_messages,
            **kwargs,
        )
        # Anthropic returns a list of content blocks
        text_blocks = [b.text for b in response.content if b.type == "text"]
        return "\n".join(text_blocks)

    async def _chat_stream_impl(
        self, model: str, messages: list[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        model = model or settings.default_llm_model
        system, chat_messages = _extract_system(messages)
        async with self._client.messages.stream(
            model=model,
            max_tokens=kwargs.pop("max_tokens", 4096),
            system=system,
            messages=chat_messages,
            **kwargs,
        ) as stream:
            async for text in stream.text_stream:
                yield text


# ── Helpers ────────────────────────────────────────────────────────────────────


def _extract_system(messages: list[dict]) -> tuple[str, list[dict]]:
    """Separate the system message from the chat history.

    Anthropic's API expects ``system`` as a top-level parameter, not as part
    of the ``messages`` list.
    """
    system_parts: list[str] = []
    chat_messages: list[dict] = []
    for msg in messages:
        if msg.get("role") == "system":
            system_parts.append(str(msg.get("content", "")))
        else:
            chat_messages.append(msg)
    return "\n".join(system_parts), chat_messages
