import React, { useState } from 'react';
import type { ManagedDocument } from '../types';
import { FiFile, FiExternalLink, FiClock, FiDownload } from 'react-icons/fi';
import { apiService } from '../services/api';

interface DocumentListProps {
  documents: ManagedDocument[];
  sessionId: string;
}

export const DocumentList: React.FC<DocumentListProps> = ({ documents, sessionId }) => {
  const [downloadingIds, setDownloadingIds] = useState<string[]>([]);
  
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
  
  const downloadDocument = async (doc: ManagedDocument) => {
    try {
      setDownloadingIds(prev => [...prev, doc.id]);
      
      const blob = await apiService.downloadDocument(doc.id, sessionId);
      
      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const a = window.document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = doc.name;
      
      // Add to the DOM and trigger download
      window.document.body.appendChild(a);
      a.click();
      
      // Cleanup
      window.URL.revokeObjectURL(url);
      window.document.body.removeChild(a);
      
    } catch (error) {
      console.error('Failed to download document:', error);
    } finally {
      setDownloadingIds(prev => prev.filter(id => id !== doc.id));
    }
  };

  return (
    // Use the concrete CSS class .document-list defined in index.css instead of Tailwind-like utilities
    <div className="document-list custom-scrollbar">
      {documents.map((doc) => (
        <div key={doc.id} className="document-item">
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
            <div className="flex items-center">
              <button
                onClick={() => downloadDocument(doc)}
                disabled={downloadingIds.includes(doc.id)}
                className="ml-2 p-1.5 text-gray-400 hover:text-green-400 disabled:opacity-50 hover:bg-gray-700 rounded transition-colors"
                title="Download document"
              >
                {downloadingIds.includes(doc.id) ? '...' : <FiDownload />}
              </button>
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
