/**
 * Agent types — mirrors backend agent/ module models.
 */

export interface Agent {
  id: string;
  user_id: string;
  name: string;
  system_prompt: string;
  model_provider: string;
  model_name: string;
  temperature: number;
  max_tokens: number;
  tool_ids: string[];
  knowledge_base_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface AgentExecution {
  id: string;
  agent_id: string;
  input: string;
  output: string | null;
  steps: AgentStep[];
  status: "running" | "completed" | "failed";
  created_at: string;
}

export interface AgentStep {
  type: "thinking" | "tool_call" | "observation" | "answer";
  content: string;
  timestamp: string;
}
