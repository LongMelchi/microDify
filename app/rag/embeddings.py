"""Embedding adapter — delegates to the provider module for batch embedding generation."""


class EmbeddingService:
    """Generates embedding vectors via the configured Embedding provider."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError
