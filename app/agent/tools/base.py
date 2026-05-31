"""Abstract tool interface for Agent tool calling."""

from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Every Agent tool MUST implement this interface."""

    name: str = ""
    description: str = ""
    parameters: dict = {}  # JSON Schema describing the tool's input parameters

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool with the given parameters and return a result string."""
        ...
