"""Start node — receives input variables and passes them downstream."""

from app.workflow.nodes.base import BaseNode


class StartNode(BaseNode):
    node_type = "start"

    async def run(self, context: dict) -> dict:
        raise NotImplementedError
