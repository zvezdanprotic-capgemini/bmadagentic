import axios from 'axios';
import type { 
  ChatRequest, 
  ChatResponse, 
  AgentsListResponse, 
  WorkflowsListResponse, 
  ManagedDocumentsResponse,
  LoginRequest,
  RegisterRequest,
  AuthResponse
} from '../types';

// Use the Vite proxy setup
const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  },
  withCredentials: false,
});

// Add a request interceptor to include auth token in requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle authentication errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      // Clear token on authentication error
      localStorage.removeItem('auth_token');
      // Add an event to notify app about auth error
      window.dispatchEvent(new CustomEvent('auth_error', {
        detail: { 
          status: error.response.status,
          message: error.response.data?.detail || 'Authentication failed'
        }
      }));
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Authentication
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post('/auth/login', credentials);
    if (response.data.token) {
      localStorage.setItem('auth_token', response.data.token);
    }
    return response.data;
  },

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  async logout(): Promise<void> {
    localStorage.removeItem('auth_token');
    // Optional: Call backend logout endpoint if needed
    // await api.post('/auth/logout');
  },

  async getCurrentUser(): Promise<AuthResponse> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // Check if the backend is running
  async healthCheck(): Promise<{ status: string }> {
    const response = await api.get('/');
    return response.data;
  },

  // Get list of available agents
  async getAgents(): Promise<AgentsListResponse> {
    const response = await api.get('/agents');
    return response.data;
  },

  // Get list of available workflows
  async getWorkflows(): Promise<WorkflowsListResponse> {
    const response = await api.get('/workflows');
    return response.data;
  },

  // Get list of managed documents
  async getDocuments(sessionId?: string): Promise<ManagedDocumentsResponse> {
    const url = sessionId ? `/documents?session_id=${sessionId}` : '/documents';
    const response = await api.get(url);
    return response.data;
  },

  // Download a specific document
  async downloadDocument(documentId: string, sessionId: string): Promise<Blob> {
    const response = await api.get(`/documents/${documentId}?session_id=${sessionId}`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Send a chat message and get response
  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post('/chat', request);
    return response.data;
  },
};