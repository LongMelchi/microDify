/**
 * Knowledge base types — mirrors backend knowledge/ and rag/ module models.
 */

export interface KnowledgeBase {
  id: string;
  user_id: string;
  name: string;
  description: string;
  document_count: number;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  knowledge_base_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: "pending" | "parsing" | "ready" | "failed";
  chunk_count: number;
  created_at: string;
}

export interface Chunk {
  id: string;
  document_id: string;
  content: string;
  index: number;
  tokens: number;
}
