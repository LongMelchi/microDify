"""Chat module API routes.

Dependencies injected via Depends(), business logic delegated to service layer.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])

# TODO: Implement endpoints:
#   POST /chat/apps              - create_chat_app
#   GET  /chat/apps              - list chat apps
#   GET  /chat/apps/{id}         - get chat app detail
#   PUT  /chat/apps/{id}         - update chat app
#   DELETE /chat/apps/{id}       - delete chat app
#   POST /chat/apps/{id}/chat    - run_chat (SSE streaming)
#   GET  /chat/apps/{id}/conversations - list conversations
#   GET  /chat/conversations/{id}/messages - list messages
