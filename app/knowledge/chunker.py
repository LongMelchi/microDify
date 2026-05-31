"""Semantic text chunker — splits documents into overlapping chunks by sentence / paragraph boundaries."""


class Chunker:
    """Splits documents into semantically-aware chunks."""

    def chunk(self, text: str, max_tokens: int = 500, overlap: int = 50) -> list[str]:
        raise NotImplementedError
