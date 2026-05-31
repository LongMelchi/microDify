"""知识库：文档上传、解析、分块。

依赖层级: Level 2
依赖白名单: core, common, auth, provider
公开导出: router, create_knowledge_base, get_knowledge_base, upload_document
"""

from app.knowledge.router import router
from app.knowledge.service import create_knowledge_base, get_knowledge_base, upload_document

__all__ = [
    "router",
    "create_knowledge_base",
    "get_knowledge_base",
    "upload_document",
]
