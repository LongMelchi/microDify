/**
 * Chat types — mirrors backend chat/ module models.
 */

export interface ChatApp {
  id: string;
  user_id: string;
  name: string;
  description: string;
  prompt_template_id: string | null;
  knowledge_base_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: string;
  chat_app_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}
