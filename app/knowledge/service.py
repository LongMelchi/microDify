"""知识库模块业务逻辑

规范:
  - async 函数，只收 db/user/业务参数
  - 不收 Request / Response / BackgroundTasks
  - 调同模块专项文件或他模块公开接口
  - 文件规模上限 400 行，超则提专项文件
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


async def get_knowledge_base(
    db: AsyncSession,
    user_id: UUID,
    kb_id: UUID,
) -> dict:
    """获取知识库详情。

    Args:
        db: 数据库会话
        user_id: 请求用户 ID
        kb_id: 知识库 ID

    Returns:
        知识库字典
    """
    # TODO: Load KB from DB → validate ownership → return serialized
    raise NotImplementedError


async def create_knowledge_base(
    db: AsyncSession,
    user_id: UUID,
    name: str,
    description: str | None = None,
) -> dict:
    """创建知识库

    Args:
        db: 数据库会话
        user_id: 创建者用户 ID
        name: 知识库名称
        description: 知识库描述（可选）

    Returns:
        创建成功的知识库字典
    """
    # TODO: 实现知识库创建逻辑
    raise NotImplementedError


async def upload_document(
    db: AsyncSession,
    user_id: UUID,
    knowledge_base_id: UUID,
    filename: str,
    file_type: str,
    file_size: int,
    file_path: str,
) -> dict:
    """上传文档到知识库

    流程: 文件落盘 → 创建 Document 记录 → Redis 入队异步处理

    Args:
        db: 数据库会话
        user_id: 上传者用户 ID
        knowledge_base_id: 目标知识库 ID
        filename: 文件名
        file_type: 文件类型（pdf|docx|txt|md|csv）
        file_size: 文件大小（字节）
        file_path: 文件存储路径

    Returns:
        创建的文档记录字典
    """
    # TODO: 实现文档创建及入队解析逻辑
    raise NotImplementedError
