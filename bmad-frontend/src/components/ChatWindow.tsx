import React, { useEffect, useRef } from 'react';
import type { ChatMessage } from '../types';
import { ChatMessageComponent } from './ChatMessage';

interface ChatWindowProps {
  messages: ChatMessage[];
  loading?: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ messages, loading = false }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="chat-window">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-gray-500 w-full">
          <div className="text-center">
            <h3 className="text-lg font-medium mb-2">Welcome to BMad Chat</h3>
            <p className="text-sm">Start a conversation with our AI agents by typing a message below.</p>
          </div>
        </div>
      ) : (
        <div className="w-full">
          {messages.map((message) => (
            <ChatMessageComponent key={message.id} message={message} />
          ))}
          {loading && (
            <div className="chat-message assistant border rounded-lg shadow-sm mb-4">
              <div className="flex flex-col">
                <div className="flex items-start p-3 bg-green-50 rounded-t-lg">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                    </div>
                  </div>
                  <div className="flex-1 min-w-0 ml-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-gray-900">BMAD Assistant</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="p-3 pt-2 text-sm text-gray-700 whitespace-pre-wrap border-t">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};