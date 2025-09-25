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

export interface AppState {
  agents: Agent[];
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sessionId: string;
}