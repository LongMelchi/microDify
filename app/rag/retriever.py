"""Unified retriever — combines vector similarity + BM25 keyword search with fusion."""


class Retriever:
    """Mixed retrieval entry point used by chat/agent/workflow modules."""

    async def search(
        self, query: str, knowledge_base_ids: list[str], top_k: int = 5
    ) -> list[dict]:
        raise NotImplementedError
