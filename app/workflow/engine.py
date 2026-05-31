"""Workflow execution engine.

Topological-sort based scheduler that walks a DAG node-by-node, resolves
variables, and returns results.
"""


class WorkflowEngine:
    """Executes a workflow definition graph."""

    # -- to be implemented -----------------------------------------------------

    async def run(self, workflow, inputs: dict):
        raise NotImplementedError
