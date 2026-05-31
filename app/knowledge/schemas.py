"""知识库模块 Pydantic 模式

命名约定:
  XxxCreate   — 创建请求
  XxxResponse — 响应
  XxxFilter   — 查询过滤

规范:
  - 只包含 Pydantic BaseModel + Field 约束
  - 不含 DB 查询、调 service
  - 文件规模上限 100 行，超则拆 schemas/
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ─── KnowledgeBase ────────────────────────────────────────────────────────────


class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""

    name: str = Field(..., min_length=1, max_length=255, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")


class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""

    id: UUID
    name: str
    description: Optional[str] = None
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeBaseFilter(BaseModel):
    """知识库查询过滤"""

    name: Optional[str] = Field(None, max_length=255, description="按名称模糊搜索")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页条数")


# ─── Document ─────────────────────────────────────────────────────────────────


class DocumentCreate(BaseModel):
    """文档创建请求（上传时使用）"""

    knowledge_base_id: UUID = Field(..., description="所属知识库 ID")
    # 文件本身通过 multipart/form-data 上传，不由 schema 承载


class DocumentResponse(BaseModel):
    """文档响应"""

    id: UUID
    knowledge_base_id: UUID
    filename: str
    file_type: str
    file_size: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentFilter(BaseModel):
    """文档查询过滤"""

    knowledge_base_id: Optional[UUID] = Field(None, description="按知识库筛选")
    status: Optional[str] = Field(None, description="按状态筛选")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页条数")


# ─── Chunk ────────────────────────────────────────────────────────────────────


class ChunkResponse(BaseModel):
    """文档分块响应"""

    id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    created_at: datetime

    model_config = {"from_attributes": True}
