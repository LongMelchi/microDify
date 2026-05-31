"""BM25 keyword search — PostgreSQL ``tsvector`` based full-text retrieval."""


class BM25Searcher:
    """Keyword-based search backed by PG ``tsvector``."""

    async def search(self, query: str, knowledge_base_ids: list[str], top_k: int = 20) -> list[dict]:
        raise NotImplementedError
