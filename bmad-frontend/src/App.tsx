import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import type { ChatMessage, AppState } from './types';
import { apiService } from './services/api';
import { FiAlertCircle, FiRefreshCw } from 'react-icons/fi';
import { Description } from './components/Description';
import { ChatWindow } from './components/ChatWindow';
import { ChatInput } from './components/ChatInput';
import { DocumentList } from './components/DocumentList';
import Header from './components/Header';
import Modal from './components/Modal';
import FigmaIntegration from './components/FigmaIntegration';

const App: React.FC = () => {
  const [state, setState] = useState<AppState>({
    agents: [],
    messages: [],
    documents: [],
    isLoading: false,
    error: null,
    sessionId: uuidv4(),
  });

  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [isFigmaModalOpen, setIsFigmaModalOpen] = useState(false);

  const fetchDocuments = async () => {
    try {
      const docsResponse = await apiService.getDocuments();
      setState(prev => ({
        ...prev,
        documents: docsResponse.documents,
      }));
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    }
  };

  useEffect(() => {
    const initializeApp = async () => {
      try {
        await apiService.healthCheck();
        setBackendStatus('online');
        const agentsResponse = await apiService.getAgents();
        setState(prev => ({ ...prev, agents: agentsResponse.agents }));
        fetchDocuments();
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
      fetchDocuments(); // Refresh documents after a response
    } catch (error) {
      const err = error as Error;
      setState(prev => ({
        ...prev,
        error: `Failed to get response: ${err.message}`,
        isLoading: false,
      }));
    }
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="app-container">
      <Header onConfigClick={() => setIsFigmaModalOpen(true)} />
      
      <main className="app-main">
        <Description
          title="BMAD Agentic Framework"
          description="This is an agentic framework for the BMAD (Build, Measure, Adapt, Disrupt) methodology. It uses a multi-agent system to automate software development tasks, from design to deployment. You can interact with the agents through this chat interface."
          agents={state.agents}
        />

        <div className="content-area">
          <aside className="document-sidebar">
            <h2 className="sidebar-title">Generated Documents</h2>
            <DocumentList documents={state.documents} />
          </aside>

          <section className="chat-area">
            <ChatWindow messages={state.messages} loading={state.isLoading} />
            <ChatInput onSendMessage={handleSendMessage} disabled={state.isLoading} />
          </section>
        </div>
      </main>

      {backendStatus === 'offline' && (
        <div className="status-overlay">
          <div className="status-box">
            <FiAlertCircle className="status-icon" />
            <p>{state.error}</p>
            <button onClick={handleRefresh} className="refresh-button">
              <FiRefreshCw />
              <span>Try Again</span>
            </button>
          </div>
        </div>
      )}

      <Modal isOpen={isFigmaModalOpen} onClose={() => setIsFigmaModalOpen(false)} title="Figma Integration">
        <FigmaIntegration sessionId={state.sessionId} onDocumentsUpdate={fetchDocuments} />
      </Modal>
    </div>
  );
};

export default App;
