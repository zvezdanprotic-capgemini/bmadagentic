import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import type { ChatMessage, AppState } from './types';
import { apiService } from './services/api';
import { FiActivity, FiAlertCircle, FiRefreshCw } from 'react-icons/fi';
import { Description } from './components/Description';
import { ChatWindow } from './components/ChatWindow';
import { ChatInput } from './components/ChatInput';

const App: React.FC = () => {
  const [state, setState] = useState<AppState>({
    agents: [],
    messages: [],
    isLoading: false,
    error: null,
    sessionId: uuidv4(),
  });

  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Check backend health and load agents on component mount
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Check if backend is running
        await apiService.healthCheck();
        setBackendStatus('online');

        // Load agents
        const agentsResponse = await apiService.getAgents();
        setState(prev => ({
          ...prev,
          agents: agentsResponse.agents,
        }));
      } catch (error) {
        console.error('Failed to initialize app:', error);
        setBackendStatus('offline');
        setState(prev => ({
          ...prev,
          error: 'Failed to connect to backend. Please make sure the backend server is running.',
        }));
      }
    };

    initializeApp();
  }, []);

  const handleSendMessage = async (messageContent: string) => {
    const userMessage: ChatMessage = {
      id: uuidv4(),
      content: messageContent,
      sender: 'user',
      timestamp: new Date(),
      isUser: true,
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: null,
    }));

    try {
      const response = await apiService.sendChatMessage({
        session_id: state.sessionId,
        message: messageContent,
      });

      const assistantMessage: ChatMessage = {
        id: uuidv4(),
        content: response.message,
        sender: response.sender,
        timestamp: new Date(),
        isUser: false,
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
      }));
    } catch (error) {
      console.error('Failed to send message:', error);
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: 'Failed to send message. Please try again.',
      }));
    }
  };

  const handleRetry = () => {
    window.location.reload();
  };

  const clearError = () => {
    setState(prev => ({ ...prev, error: null }));
  };

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">BMad Agentic System</h1>
              <div className="ml-4 flex items-center">
                <div className={`w-2 h-2 rounded-full mr-2 ${
                  backendStatus === 'online' ? 'bg-green-400' : 
                  backendStatus === 'offline' ? 'bg-red-400' : 'bg-yellow-400'
                }`}></div>
                <span className="text-sm text-gray-600">
                  Backend: {backendStatus === 'checking' ? 'Checking...' : backendStatus}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <FiActivity className="w-5 h-5 text-primary-600" />
              <span className="text-sm text-gray-600">Session: {state.sessionId.slice(0, 8)}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {state.error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <FiAlertCircle className="h-5 w-5 text-red-400" />
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm text-red-700">{state.error}</p>
            </div>
            <div className="ml-auto pl-3">
              <div className="flex space-x-2">
                <button
                  onClick={handleRetry}
                  className="text-red-700 hover:text-red-600 text-sm font-medium"
                >
                  <FiRefreshCw className="w-4 h-4" />
                </button>
                <button
                  onClick={clearError}
                  className="text-red-700 hover:text-red-600 text-sm font-medium"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Vertical Layout Structure */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Description Section with BMAD Method Info */}
        <div className="w-full px-4 pt-4 pb-2">
          <div className="w-full mx-auto" style={{ maxWidth: "1200px" }}>
            <Description 
              title="BMAD Method - Universal AI Agent Framework"
              agents={state.agents}
              description={`The BMAD Method is a comprehensive AI agent framework for agile development and task management. Users can interact with this agentic system in the following ways:

1. **Command-Based Communication**: Type commands with an asterisk prefix (e.g., *help, *agent, *status) to control the system. The *help command shows all available options.

2. **Agent Transformation**: Use *agent [name] to transform into specialized roles like Analyst, PM, Developer, Architect, etc. Each agent has unique expertise and capabilities.

3. **Task Execution**: Run *task [name] to execute specific workflows like creating documents or analyzing requirements.

4. **Interactive Modes**: Choose between Incremental Mode (step-by-step with user input) or YOLO Mode (rapid generation with minimal interaction).

5. **Knowledge Base Access**: Use *kb-mode to access the full BMAD knowledge base for detailed guidance.

This chat interface allows you to communicate with the BMAD agentic system directly. Start by typing a message or command below.`}
            />
          </div>
        </div>

        {/* Chat Window Area */}
        <div className="flex-1 flex flex-col overflow-hidden w-full mx-auto px-4" style={{ maxWidth: "1200px" }}>
          <div className="flex-1 overflow-y-auto w-full">
            <ChatWindow messages={state.messages} loading={state.isLoading} />
          </div>
          <div className="w-full">
            <ChatInput
              onSendMessage={handleSendMessage}
              disabled={backendStatus !== 'online'}
              loading={state.isLoading}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
