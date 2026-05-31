"""知识库 API 路由

规范:
- 只声明路径/方法、注入 Depends、调 service 并返回
- 不包含 DB 查询、ORM、业务逻辑
- 文件规模上限 150 行，超则拆子路由
"""

from fastapi import APIRouter

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# TODO: 注册知识库 CRUD 端点
# TODO: 注册文档上传端点
