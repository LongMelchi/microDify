"""RAG 模块 Pydantic 请求/响应模型。

命名约定（遵循 CLAUDE.md §3）：
- XxxCreate : 创建请求
- XxxResponse: 响应
- XxxFilter : 查询/过滤参数
"""

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """检索请求参数。"""

    query: str = Field(..., min_length=1, description="检索 query 文本")
    knowledge_base_id: str = Field(..., description="目标知识库 ID")
    top_k: int = Field(default=5, ge=1, le=50, description="返回 top-k 块")
    use_rerank: bool = Field(default=True, description="是否启用重排序")


class ChunkResult(BaseModel):
    """单条检索结果。"""

    chunk_id: str = Field(..., description="chunk ID")
    document_id: str = Field(..., description="所属文档 ID")
    content: str = Field(..., description="chunk 文本内容")
    score: float = Field(..., ge=0.0, le=1.0, description="相关性分数")
    rerank_score: float | None = Field(default=None, description="重排序后分数")


class SearchResponse(BaseModel):
    """检索响应。"""

    results: list[ChunkResult] = Field(default_factory=list)
    total: int = Field(..., ge=0, description="匹配总数")
    query: str = Field(..., description="原始查询")
