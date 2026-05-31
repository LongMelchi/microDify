# workflow/schemas.py
# Pydantic schemas for the workflow module.
# Only BaseModel + Field — no DB queries, no service calls.
# Max 100 lines; split into schemas/ directory when exceeded.
#
# Naming convention (three suffixes):
#   XxxCreate   — request body for creation / update
#   XxxResponse — response body returned to client
#   XxxFilter   — query-string / filter parameters for listing

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# Workflow ──────────────────────────────────────────────────────────────

class WorkflowCreate(BaseModel):
    """Request schema for creating a new workflow."""
    name: str = Field(..., min_length=1, max_length=255, description="Workflow name")
    description: str = Field("", max_length=500, description="Optional description")

class WorkflowResponse(BaseModel):
    """Response schema for a workflow."""
    id: str = Field(..., description="UUID of the workflow")
    user_id: str = Field(..., description="UUID of the owner")
    name: str = Field(..., description="Workflow name")
    description: str = Field("", description="Optional description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class WorkflowFilter(BaseModel):
    """Filter / query parameters for listing workflows."""
    name: str | None = Field(None, max_length=255, description="Filter by name (partial match)")

# Node ─────────────────────────────────────────────────────────────────

class WorkflowNodeCreate(BaseModel):
    """Request schema for adding a node to a workflow."""
    type: str = Field(..., description="Node type: start, llm, knowledge_retrieval, condition, variable_transform, end")
    label: str = Field("", max_length=255, description="Display label for the node")
    config: dict[str, Any] = Field(default_factory=dict, description="Type-specific configuration")
    position_x: int = Field(0, description="Canvas X position")
    position_y: int = Field(0, description="Canvas Y position")

class WorkflowNodeResponse(BaseModel):
    """Response schema for a workflow node."""
    id: str = Field(..., description="UUID of the node")
    workflow_id: str = Field(..., description="UUID of the parent workflow")
    type: str = Field(..., description="Node type")
    label: str = Field("", description="Display label")
    config: dict[str, Any] = Field(default_factory=dict, description="Node configuration")
    position_x: int = Field(0, description="Canvas X position")
    position_y: int = Field(0, description="Canvas Y position")
    created_at: datetime = Field(..., description="Creation timestamp")

# Edge ─────────────────────────────────────────────────────────────────

class WorkflowEdgeCreate(BaseModel):
    """Request schema for creating an edge between nodes."""
    source_node_id: str = Field(..., description="UUID of the source node")
    target_node_id: str = Field(..., description="UUID of the target node")
    condition_expression: str = Field("", description="Optional condition expression for branching")
    label: str = Field("", max_length=255, description="Display label")

class WorkflowEdgeResponse(BaseModel):
    """Response schema for a workflow edge."""
    id: str = Field(..., description="UUID of the edge")
    workflow_id: str = Field(..., description="UUID of the parent workflow")
    source_node_id: str = Field(..., description="UUID of the source node")
    target_node_id: str = Field(..., description="UUID of the target node")
    condition_expression: str = Field("", description="Branch condition expression")
    label: str = Field("", description="Display label")
    created_at: datetime = Field(..., description="Creation timestamp")

# Execution ────────────────────────────────────────────────────────────

class WorkflowExecutionResponse(BaseModel):
    """Response schema for a workflow execution record."""
    id: str = Field(..., description="UUID of the execution")
    workflow_id: str = Field(..., description="UUID of the workflow")
    user_id: str = Field(..., description="UUID of the user who triggered execution")
    status: str = Field(..., description="pending, running, completed, failed, cancelled")
    input_data: dict[str, Any] = Field(default_factory=dict, description="Execution input")
    output_data: dict[str, Any] | None = Field(None, description="Execution output")
    node_results: list[dict[str, Any]] | None = Field(None, description="Per-node execution results")
    error_message: str | None = Field(None, description="Error message if failed")
    started_at: datetime | None = Field(None, description="Execution start time")
    finished_at: datetime | None = Field(None, description="Execution finish time")
    created_at: datetime = Field(..., description="Record creation time")
