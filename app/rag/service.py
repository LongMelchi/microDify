"""RAG 引擎服务：混合检索、重排序、嵌入。

公开类
--------
Retriever : 知识库混合检索入口，封装 BM25 + 向量检索 + Rerank。
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.schemas import ChunkResult, SearchResponse


class Retriever:
    """RAG 混合检索引擎。

    职责
    ----
    - 接收 query + knowledge_base_id，执行 BM25 / 向量混合检索
    - 合并结果并重排序
    - 返回 CORE 模块可消费的 ID 级结果
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def search(
        self,
        query: str,
        knowledge_base_id: str,
        top_k: int = 5,
        use_rerank: bool = True,
    ) -> SearchResponse:
        """执行混合检索，可选 rerank。

        Parameters
        ----------
        query : str
            用户 query 文本。
        knowledge_base_id : str
            目标知识库 ID。
        top_k : int
            返回 top-k 个 chunk，默认 5。
        use_rerank : bool
            是否对召回结果执行重排序，默认 True。

        Returns
        -------
        SearchResponse
            检索结果包含 chunk 列表和元信息。
        """

        # TODO: 实现 BM25 全文检索（pg tsvector）
        # TODO: 实现向量检索（pgvector cosine / inner product）
        # TODO: 实现 RRF / weighted 融合
        # TODO: 可选 rerank（LLM 或 lightweight cross-encoder）
        chunks: Sequence[ChunkResult] = []
        return SearchResponse(
            results=list(chunks),
            total=len(chunks),
            query=query,
        )

    async def rerank(
        self,
        query: str,
        chunks: Sequence[ChunkResult],
        top_k: int | None = None,
    ) -> Sequence[ChunkResult]:
        """对检索结果执行重排序。

        Parameters
        ----------
        query : str
            原始 query。
        chunks : Sequence[ChunkResult]
            待重排序的候选结果。
        top_k : int | None
            返回前 k 条；为 None 时返回全部。

        Returns
        -------
        Sequence[ChunkResult]
            按 rerank_score 降序排列的结果。
        """

        # TODO: 实现 lightweight cross-encoder 或 LLM rerank
        top_k = top_k or len(chunks)
        return sorted(chunks, key=lambda c: c.score or 0.0, reverse=True)[:top_k]
