/**
 * Workflow types — mirrors backend workflow/ module models.
 */

export interface Workflow {
  id: string;
  user_id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export type NodeType =
  | "start"
  | "llm"
  | "knowledge_retrieval"
  | "condition"
  | "variable_transform"
  | "end";

export interface WorkflowNode {
  id: string;
  workflow_id: string;
  type: NodeType;
  label: string;
  config: Record<string, unknown>;
  position_x: number;
  position_y: number;
}

export interface WorkflowEdge {
  id: string;
  workflow_id: string;
  source_node_id: string;
  target_node_id: string;
  condition_expression: string | null;
}
