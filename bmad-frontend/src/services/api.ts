import axios from 'axios';
import type { ChatRequest, ChatResponse, AgentsListResponse, WorkflowsListResponse } from '../types';

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

export const apiService = {
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

  // Send a chat message and get response
  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post('/chat', request);
    return response.data;
  },
};