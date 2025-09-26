import React from 'react';
import type { ManagedDocument } from '../types';
import { FiFile, FiExternalLink, FiClock } from 'react-icons/fi';

interface DocumentListProps {
  documents: ManagedDocument[];
}

export const DocumentList: React.FC<DocumentListProps> = ({ documents }) => {
  if (documents.length === 0) {
    return (
      <div className="text-center text-gray-500 py-4">
        <p>No documents have been generated yet.</p>
      </div>
    );
  }

  const formatTimestamp = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="space-y-3 overflow-y-auto max-h-96 pr-2">
      {documents.map((doc) => (
        <div key={doc.id} className="bg-gray-800 p-3 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors duration-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center overflow-hidden">
              <FiFile className="text-gray-400 mr-3 flex-shrink-0" />
              <div className="flex flex-col overflow-hidden">
                <span className="font-semibold text-sm truncate" title={doc.name}>
                  {doc.name}
                </span>
                <span className="text-xs text-gray-400">{doc.type}</span>
              </div>
            </div>
            {doc.external_url && (
              <a
                href={doc.external_url}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 p-1 text-gray-400 hover:text-blue-400"
                title="Open in new tab"
              >
                <FiExternalLink />
              </a>
            )}
          </div>
          <div className="flex items-center justify-between text-xs text-gray-500 mt-2">
            <span>Source: {doc.source}</span>
            <div className="flex items-center">
              <FiClock className="mr-1" />
              <span>{formatTimestamp(doc.created_at)}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
