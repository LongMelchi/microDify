"""Abstract node interface for workflow nodes."""

from abc import ABC, abstractmethod


class BaseNode(ABC):
    """Every workflow node type MUST implement this interface."""

    node_type: str = ""

    @abstractmethod
    async def run(self, context: dict) -> dict:
        """Execute the node with the given *context* and return updated context."""
        ...
