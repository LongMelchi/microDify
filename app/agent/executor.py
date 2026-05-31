"""ReAct reasoning loop executor.

Orchestrates the Thought → Action → Observation cycle for an Agent execution.
Injected with the :class:`LLMGateway`, :class:`Retriever`, and a
:class:`ToolRegistry`.
"""

from app.core.exceptions import ErrorCode


class AgentExecutor:
    """Executes a single Agent run using the ReAct protocol."""

    # -- to be implemented -----------------------------------------------------

    async def run(self, agent, user_input: str):
        raise NotImplementedError
