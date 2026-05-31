"""LLM node — calls the :class:`LLMGateway` with a prompt template."""

from app.workflow.nodes.base import BaseNode


class LLMNode(BaseNode):
    node_type = "llm"

    async def run(self, context: dict) -> dict:
        raise NotImplementedError
