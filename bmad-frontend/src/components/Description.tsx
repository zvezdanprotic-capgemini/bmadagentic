import React, { useState } from 'react';
import { FiChevronDown, FiChevronUp, FiUsers, FiInfo } from 'react-icons/fi';
import { AgentList } from './AgentList';
import type { Agent } from '../types';

interface DescriptionProps {
  title: string;
  description: string;
  agents?: Agent[];
}

export const Description: React.FC<DescriptionProps> = ({ title, description, agents = [] }) => {
  const [isDescExpanded, setIsDescExpanded] = useState(true);
  const [isAgentExpanded, setIsAgentExpanded] = useState(false);

  return (
    <div className="bg-white shadow rounded-lg mb-4 w-full max-w-none">
      {/* Description Section */}
      <div 
        className="p-4 flex justify-between items-center cursor-pointer bg-gradient-to-r from-blue-50 to-blue-100"
        onClick={() => setIsDescExpanded(!isDescExpanded)}
      >
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <FiInfo className="mr-2" /> {title}
        </h2>
        <button className="text-gray-500 hover:text-gray-700 focus:outline-none">
          {isDescExpanded ? <FiChevronUp className="w-5 h-5" /> : <FiChevronDown className="w-5 h-5" />}
        </button>
      </div>
      
      {isDescExpanded && (
        <div className="px-6 pb-6 pt-2">
          <div className="border-t border-gray-200 pt-3">
            <div className="max-w-none text-gray-700">
              {description.split('\n\n').map((paragraph, i) => {
                if (paragraph.startsWith('1.') || paragraph.startsWith('2.') || paragraph.startsWith('3.') || 
                    paragraph.startsWith('4.') || paragraph.startsWith('5.')) {
                  // Handle numbered lists with bold headings
                  const parts = paragraph.split('**');
                  if (parts.length >= 3) {
                    return (
                      <div key={i} className="my-3">
                        <p><strong>{parts[1]}</strong>{parts[2]}</p>
                      </div>
                    );
                  }
                }
                return <p key={i} className="my-3">{paragraph}</p>;
              })}
            </div>
          </div>
        </div>
      )}
      
      {/* Agents Section */}
      {agents && agents.length > 0 && (
        <>
          <div 
            className="px-4 py-3 border-t border-gray-200 flex justify-between items-center cursor-pointer"
            onClick={() => setIsAgentExpanded(!isAgentExpanded)}
          >
            <h3 className="font-medium text-gray-900 flex items-center">
              <FiUsers className="mr-2" /> Available Agents ({agents.length})
            </h3>
            <button className="text-gray-500 hover:text-gray-700 focus:outline-none">
              {isAgentExpanded ? <FiChevronUp className="w-5 h-5" /> : <FiChevronDown className="w-5 h-5" />}
            </button>
          </div>
          
          {isAgentExpanded && (
            <div className="px-4 pb-4">
              <div className="space-y-3">
                {agents.map((agent) => (
                  <div
                    key={agent.id}
                    className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">{agent.name}</h4>
                        <p className="text-sm text-gray-600">{agent.title}</p>
                      </div>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                        {agent.id}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">{agent.when_to_use}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};