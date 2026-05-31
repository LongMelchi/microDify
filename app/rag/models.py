"""RAG 模块数据模型。

注意：RAG 引擎不产生独立数据表。它直接通过 pgvector
操作 knowledge.chunks 表的 embedding 列完成向量检索，
通过 PostgreSQL 全文检索（tsvector）完成 BM25 关键词匹配。

此处仅预留 Base Model 桩以供 Alembic 自动发现；业务表定义
位于 knowledge/models.py（chunks 表）。
"""

from app.core.database import Base

# RAG 模块不新增业务表。
# 混合检索操作对象：knowledge_chunks.embedding (vector)
#                    knowledge_chunks.document_id (FK)
#                    knowledge_chunks.content (text)
#                    knowledge_chunks.tsvector (tsvector, 全文索引)
