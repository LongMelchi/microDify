/**
 * Prompt template types — mirrors backend prompt/ module models.
 */

export interface PromptTemplate {
  id: string;
  user_id: string;
  name: string;
  content: string;
  variables: string[];
  created_at: string;
  updated_at: string;
}
