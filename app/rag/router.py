"""RAG API 路由。

当前无端点，仅声明 APIRouter 供 main.py 注册。
"""

from fastapi import APIRouter

router = APIRouter(prefix="/rag", tags=["rag"])
