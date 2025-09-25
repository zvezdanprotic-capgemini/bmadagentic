import React, { useState } from 'react';
import { FiSend, FiLoader } from 'react-icons/fi';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  loading?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  disabled = false, 
  loading = false 
}) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled && !loading) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="sticky bottom-0 border-t border-gray-200 bg-white shadow-lg p-4 w-full">
      <form onSubmit={handleSubmit} className="w-full">
        <div className="flex space-x-3 w-full">
          <div className="flex-1 w-full">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={disabled}
              placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none shadow-sm"
              rows={2}
              style={{ minHeight: '60px' }}
            />
          </div>
          <button
            type="submit"
            disabled={disabled || loading || !message.trim()}
            className="bg-primary-600 hover:bg-primary-700 text-white disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center rounded-lg px-6"
          >
            {loading ? (
              <FiLoader className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <FiSend className="w-5 h-5 mr-2" />
                <span>Send</span>
              </>
            )}
          </button>
        </div>
        <div className="text-xs text-gray-500 mt-2 text-center">
          {disabled ? 'Backend is offline. Please start the server.' : 'Press Enter to send, Shift+Enter for new line'}
        </div>
      </form>
    </div>
  );
}