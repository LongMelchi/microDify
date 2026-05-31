"""Condition node — evaluates an if/else expression to route the DAG."""

from app.workflow.nodes.base import BaseNode


class ConditionNode(BaseNode):
    node_type = "condition"

    async def run(self, context: dict) -> dict:
        raise NotImplementedError
