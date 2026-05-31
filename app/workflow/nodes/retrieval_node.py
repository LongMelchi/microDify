"""Knowledge-retrieval node — searches pgvector + BM25 via the RAG module."""

from app.workflow.nodes.base import BaseNode


class RetrievalNode(BaseNode):
    node_type = "retrieval"

    async def run(self, context: dict) -> dict:
        raise NotImplementedError
