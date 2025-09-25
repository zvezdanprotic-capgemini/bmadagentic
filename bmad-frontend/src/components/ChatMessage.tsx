import React, { useState } from 'react';
import type { ChatMessage } from '../types';
import { FiUser, FiCpu, FiChevronDown, FiChevronUp } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';

interface ChatMessageProps {
  message: ChatMessage;
}

export const ChatMessageComponent: React.FC<ChatMessageProps> = ({ message }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className={`chat-message ${message.isUser ? 'user' : 'assistant'} border rounded-lg shadow-sm mb-4`}>
      <div className="flex flex-col">
        <div 
          className={`flex items-start p-3 ${message.isUser ? 'bg-blue-50' : 'bg-green-50'} rounded-t-lg`}
        >
          <div className="flex-shrink-0">
            {message.isUser ? (
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                <FiUser className="w-4 h-4 text-white" />
              </div>
            ) : (
              <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
                <FiCpu className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0 ml-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <p className="text-sm font-medium text-gray-900">
                  {message.isUser ? 'You' : message.sender || 'BMAD Assistant'}
                </p>
                <p className="text-xs text-gray-500">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
              <button
                className="text-gray-500 hover:text-gray-700 focus:outline-none"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? <FiChevronUp className="w-4 h-4" /> : <FiChevronDown className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>
        {isExpanded && (
          <div className="p-4 pt-3 text-sm text-gray-700 border-t">
            {message.isUser ? (
              <div className="whitespace-pre-wrap">{message.content}</div>
            ) : (
              <div className="markdown-content">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};