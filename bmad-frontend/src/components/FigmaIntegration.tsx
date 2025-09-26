import React, { useState } from 'react';

interface FigmaIntegrationProps {
  sessionId: string;
  onDocumentsUpdate?: () => void;
}

const FigmaIntegration: React.FC<FigmaIntegrationProps> = ({ sessionId, onDocumentsUpdate }) => {
  const [figmaToken, setFigmaToken] = useState('');
  const [fileId, setFileId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  const storeFigmaCredentials = async () => {
    if (!figmaToken) {
      setError('Please enter your Figma personal access token');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/credentials', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          service: 'figma',
          credentials: {
            token: figmaToken,
            email: ''
          }
        })
      });

      if (!response.ok) {
        throw new Error('Failed to store credentials');
      }

      setError('');
      alert('Figma credentials stored successfully!');
    } catch (err) {
      setError(`Error storing credentials: ${err.message}`);
    }
  };

  const getComponents = async () => {
    if (!fileId) {
      setError('Please enter a Figma file ID');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/figma/components', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          file_id: fileId
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to fetch components');
      }

      setResults({
        type: 'components',
        data: data
      });

      // Refresh documents list
      if (onDocumentsUpdate) {
        onDocumentsUpdate();
      }
    } catch (err) {
      setError(`Error fetching components: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const getUserFlows = async () => {
    if (!fileId) {
      setError('Please enter a Figma file ID');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/figma/user-flows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          file_id: fileId
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to fetch user flows');
      }

      setResults({
        type: 'user_flows',
        data: data
      });

      // Refresh documents list
      if (onDocumentsUpdate) {
        onDocumentsUpdate();
      }
    } catch (err) {
      setError(`Error fetching user flows: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="figma-integration p-4 border border-gray-300 rounded-lg mb-4">
      <h3 className="text-lg font-bold mb-4">Figma Integration</h3>
      
      {/* Credentials Section */}
      <div className="mb-4">
        <h4 className="font-semibold mb-2">Setup Credentials</h4>
        <div className="flex gap-2 mb-2">
          <input
            type="password"
            value={figmaToken}
            onChange={(e) => setFigmaToken(e.target.value)}
            placeholder="Enter your Figma personal access token"
            className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={storeFigmaCredentials}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Store Token
          </button>
        </div>
        <p className="text-sm text-gray-600">
          Get your token from <a href="https://figma.com/developers/api#access-tokens" target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">Figma Developer Settings</a>
        </p>
      </div>

      {/* File ID Section */}
      <div className="mb-4">
        <h4 className="font-semibold mb-2">Figma File</h4>
        <input
          type="text"
          value={fileId}
          onChange={(e) => setFileId(e.target.value)}
          placeholder="Enter Figma file ID (e.g., ABC123def456)"
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
        />
        <p className="text-sm text-gray-600">
          Find the file ID in your Figma file URL: figma.com/file/<strong>FILE_ID</strong>/filename
        </p>
      </div>

      {/* Actions */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={getComponents}
          disabled={isLoading || !fileId}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-400"
        >
          {isLoading ? 'Loading...' : 'Get Components'}
        </button>
        <button
          onClick={getUserFlows}
          disabled={isLoading || !fileId}
          className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-400"
        >
          {isLoading ? 'Loading...' : 'Get User Flows'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Results Display */}
      {results && (
        <div className="bg-gray-50 p-4 rounded">
          <h4 className="font-semibold mb-2">
            {results.type === 'components' ? 'Components Found' : 'User Flows Found'}
          </h4>
          
          {results.type === 'components' && (
            <div>
              <p className="mb-2">File: <strong>{results.data.file_name}</strong></p>
              <p className="mb-2">Total Components: <strong>{results.data.total_components}</strong></p>
              <p className="mb-2">Document ID: <strong>{results.data.document_id}</strong></p>
              
              {results.data.components && results.data.components.length > 0 && (
                <div>
                  <p className="font-medium mb-1">Components:</p>
                  <ul className="list-disc list-inside max-h-40 overflow-y-auto">
                    {results.data.components.map((component, index) => (
                      <li key={index} className="text-sm">
                        <strong>{component.name}</strong> ({component.type})
                        {component.parent && <span className="text-gray-600"> - in {component.parent}</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {results.type === 'user_flows' && (
            <div>
              <p className="mb-2">File: <strong>{results.data.file_name}</strong></p>
              <p className="mb-2">Total Screens: <strong>{results.data.total_screens}</strong></p>
              <p className="mb-2">Total Flows: <strong>{results.data.total_flows}</strong></p>
              <p className="mb-2">Document ID: <strong>{results.data.document_id}</strong></p>
              
              {results.data.screens && results.data.screens.length > 0 && (
                <div className="mb-3">
                  <p className="font-medium mb-1">Screens:</p>
                  <ul className="list-disc list-inside max-h-32 overflow-y-auto">
                    {results.data.screens.map((screen, index) => (
                      <li key={index} className="text-sm">
                        <strong>{screen.name}</strong>
                        {screen.parent && <span className="text-gray-600"> - in {screen.parent}</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {results.data.user_flows && results.data.user_flows.length > 0 && (
                <div>
                  <p className="font-medium mb-1">Flow Connectors:</p>
                  <ul className="list-disc list-inside max-h-32 overflow-y-auto">
                    {results.data.user_flows.map((flow, index) => (
                      <li key={index} className="text-sm">
                        <strong>{flow.name}</strong> ({flow.type})
                        {flow.parent && <span className="text-gray-600"> - in {flow.parent}</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FigmaIntegration;