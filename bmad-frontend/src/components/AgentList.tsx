import React, { useState } from 'react';
import type { Agent } from '../types';
import { FiUsers, FiChevronDown, FiChevronUp } from 'react-icons/fi';

interface AgentListProps {
  agents: Agent[];
  loading: boolean;
}

export const AgentList: React.FC<AgentListProps> = ({ agents, loading }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h2 className="text-lg font-medium text-gray-900 flex items-center justify-between">
            <div className="flex items-center">
              <FiUsers className="w-5 h-5 mr-2" />
              Available Agents
            </div>
          </h2>
        </div>
        <div className="p-4">
          <div className="animate-pulse space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div 
        className="p-4 border-b flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <h2 className="text-lg font-medium text-gray-900 flex items-center">
          <FiUsers className="w-5 h-5 mr-2" />
          Available Agents ({agents.length})
        </h2>
        <button className="text-gray-500 hover:text-gray-700 focus:outline-none">
          {isExpanded ? <FiChevronUp className="w-5 h-5" /> : <FiChevronDown className="w-5 h-5" />}
        </button>
      </div>
      {isExpanded && (
        <div className="p-4">
          <div className="space-y-3">
            {agents.length === 0 ? (
              <p className="text-gray-500 text-sm">No agents available</p>
            ) : (
              agents.map((agent) => (
                <div
                  key={agent.id}
                  className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{agent.name}</h3>
                      <p className="text-sm text-gray-600">{agent.title}</p>
                    </div>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                      {agent.id}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">{agent.when_to_use}</p>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}