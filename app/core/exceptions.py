"""Unified exception hierarchy for microDify.

Usage::

    from app.core.exceptions import ErrorCode, BizException

    raise BizException(ErrorCode.NOT_FOUND, detail="用户不存在")
    # → HTTP 404, body: {"code": 404, "message": "用户不存在", "data": null}
"""

from enum import Enum


# ── Error codes ────────────────────────────────────────────────────────────────


class ErrorCode(Enum):
    """Error code registry.

    Every error code carries an ``(int, str)`` tuple: ``(http_status, default_message)``.
    Access via ``.value`` or use the convenience properties on ``BizException``.
    """

    # ── General errors ─────────────────────────────────────────────────────
    BAD_REQUEST = (400, "请求参数有误")
    UNAUTHORIZED = (401, "未登录或登录已过期")
    FORBIDDEN = (403, "没有访问权限")
    NOT_FOUND = (404, "资源不存在")
    METHOD_NOT_ALLOWED = (405, "不支持的请求方法")
    TOO_MANY_REQUESTS = (429, "请求过于频繁，请稍后重试")

    # ── Server errors ───────────────────────────────────────────────────────
    INTERNAL_ERROR = (500, "系统内部错误，请稍后重试")

    # ── Business errors ─────────────────────────────────────────────────────
    LLM_ERROR = (502, "AI 服务暂时不可用，请稍后重试")
    RAG_ERROR = (502, "知识库检索失败")
    KNOWLEDGE_PARSE_ERROR = (422, "文档解析失败，请检查文件格式")
    WORKFLOW_EXECUTE_ERROR = (500, "工作流执行失败")
    AGENT_TOOL_ERROR = (502, "Agent 工具调用失败")


# ── Business exception ─────────────────────────────────────────────────────────


class BizException(Exception):
    """Business exception that carries an ``ErrorCode`` and an optional detail override.

    Raise this in service layers — never in routers.  The global exception handler
    in ``main.py`` translates it into a ``Result.fail()`` JSON response.

    Usage::

        raise BizException(ErrorCode.NOT_FOUND)
        raise BizException(ErrorCode.NOT_FOUND, detail="对话应用不存在")
    """

    def __init__(self, error_code: ErrorCode, *, detail: str | None = None) -> None:
        self.error_code = error_code
        self.detail: str = detail or error_code.value[1]

    @property
    def code(self) -> int:
        """HTTP status code derived from the error code."""
        return self.error_code.value[0]

    @property
    def message(self) -> str:
        """Human-readable message, possibly overridden by *detail*."""
        return self.detail

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"
