"""Variable-transform node — Jinja2 template rendering / type casting."""

from app.workflow.nodes.base import BaseNode


class VariableNode(BaseNode):
    node_type = "variable"

    async def run(self, context: dict) -> dict:
        raise NotImplementedError
