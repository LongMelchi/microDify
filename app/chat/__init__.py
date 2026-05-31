"""Chat module: SSE streaming dialogue applications.

Public exports:
- router: APIRouter for /chat endpoints
- create_chat_app: Create a new chat application
- run_chat: Execute a streaming chat conversation
"""

from app.chat.router import router
from app.chat.service import create_chat_app, run_chat

__all__ = [
    "router",
    "create_chat_app",
    "run_chat",
]
