"""模型提供商：OpenAI + Anthropic 适配，统一 LLMGateway。

Public exports:
    LLMGateway — unified entry point for LLM and embedding operations
    BaseLLMProvider — abstract base for LLM adapters
    ProviderRegistry — registry of named adapter instances
"""

from app.provider.base import BaseEmbeddingProvider, BaseLLMProvider
from app.provider.registry import LLMGateway, ProviderRegistry
from app.provider.router import router

__all__ = [
    "BaseEmbeddingProvider",
    "BaseLLMProvider",
    "LLMGateway",
    "ProviderRegistry",
    "router",
]
