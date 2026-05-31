# workflow/service.py
# 工作流业务逻辑
#
# Public exports (via __init__.py):
#   create_workflow — create a new workflow definition
#   run_workflow    — execute a workflow end-to-end
#
# Dependency whitelist: core, auth, provider, rag, prompt
#
# Signature rules:
#   - async only
#   - params: db, user (optional), business arguments
#   - NEVER accept Request/Response/BackgroundTasks

import uuid

from sqlalchemy.ext.asyncio import AsyncSession


async def get_workflow(
    db: AsyncSession,
    user_id: uuid.UUID,
    workflow_id: uuid.UUID,
) -> dict:
    """Get a workflow definition by ID."""
    # TODO: Load workflow with nodes and edges → validate ownership → return serialized
    raise NotImplementedError("get_workflow not yet implemented")


async def create_workflow(
    db: AsyncSession,
    user_id: uuid.UUID,
    name: str,
    description: str = "",
) -> uuid.UUID:
    """Create a new workflow definition.

    Args:
        db: Database session.
        user_id: UUID of the owning user.
        name: Workflow name.
        description: Optional description.

    Returns:
        UUID of the newly created workflow.
    """
    # TODO: validate name uniqueness → create Workflow row → return id
    ...


async def run_workflow(
    db: AsyncSession,
    user_id: uuid.UUID,
    workflow_id: uuid.UUID,
    input_data: dict,
) -> uuid.UUID:
    """Execute a workflow from start to end.

    Args:
        db: Database session.
        user_id: UUID of the user triggering execution.
        workflow_id: UUID of the workflow to run.
        input_data: Initial input payload passed to the start node.

    Returns:
        UUID of the workflow execution record.
    """
    # TODO:
    #   1. Load workflow with nodes and edges
    #   2. Validate graph topology (single start, reachable end, no cycles)
    #   3. Create WorkflowExecution record (status=running)
    #   4. Walk nodes in topological order, executing each:
    #      - LLM node  → call provider via LLMGateway
    #      - knowledge_retrieval node → call rag service
    #      - condition node  → evaluate expression, pick branch
    #      - variable_transform node → apply variable mapping
    #      - start/end nodes → pass-through
    #   5. Update WorkflowExecution with results and status
    #   6. Return execution id
    ...
