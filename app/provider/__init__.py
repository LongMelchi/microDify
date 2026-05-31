"""Provider module: LLM provider adapters and unified gateway.

Dependency level: 1 (whitelist: core/)
Internal files: base.py, openai_provider.py, anthropic_provider.py, registry.py

Public exports:
    LLMGateway — unified async interface for LLM calls (chat + embedding)
    BaseLLMProvider — abstract base for LLM adapters
"""

from app.provider.base import BaseLLMProvider
from app.provider.registry import LLMGateway

__all__ = [
    "LLMGateway",
    "BaseLLMProvider",
]
