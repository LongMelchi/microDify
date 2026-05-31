"""Re-ranker — refines retrieval results with a cross-encoder or rule-based scorer."""


class Reranker:
    """Re-ranks a candidate list of chunks to improve relevance."""

    def rerank(self, query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
        raise NotImplementedError
