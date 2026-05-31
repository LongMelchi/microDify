"""End node — collects and returns the final output of a workflow."""

from app.workflow.nodes.base import BaseNode


class EndNode(BaseNode):
    node_type = "end"

    async def run(self, context: dict) -> dict:
        raise NotImplementedError
