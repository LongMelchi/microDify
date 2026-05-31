"""RAG 引擎：pgvector 混合检索、Rerank。

对外公开符号：
    Retriever — 统一检索入口，封装向量检索 + BM25 + 重排序
"""

from app.rag.retriever import Retriever

__all__ = [
    "Retriever",
]
