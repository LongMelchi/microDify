"""Agent 智能体：ReAct 推理 + 工具调用 + 知识库绑定

Public exports:
    router — APIRouter registered under /agent
    create_agent — Create a new agent configuration
    get_agent — Get an agent by ID
    run_agent — Execute an agent with ReAct reasoning loop
"""

from app.agent.router import router
from app.agent.service import create_agent, get_agent, run_agent

__all__ = [
    "router",
    "create_agent",
    "get_agent",
    "run_agent",
]
