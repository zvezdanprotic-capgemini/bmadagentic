export interface Agent {
  id: string;
  name: string;
  title: string;
  when_to_use: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: string;
  timestamp: Date;
  isUser: boolean;
}

export interface ChatRequest {
  session_id: string;
  message: string;
}

export interface ChatResponse {
  message: string;
  sender: string;
}

export interface AgentsListResponse {
  agents: Agent[];
}

export interface WorkflowsListResponse {
  workflows: any[];
}

export interface ManagedDocument {
  id: string;
  name: string;
  type: string;
  source: string;
  external_url: string | null;
  local_path: string | null;
  created_at: string;
  metadata: Record<string, any>;
}

export interface ManagedDocumentsResponse {
  documents: ManagedDocument[];
}

export interface AppState {
  agents: Agent[];
  messages: ChatMessage[];
  documents: ManagedDocument[];
  isLoading: boolean;
  error: string | null;
  sessionId: string;
}