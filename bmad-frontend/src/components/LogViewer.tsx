import React, { useEffect, useState, useCallback } from 'react';
import { apiService } from '../services/api';
import { FiFileText, FiChevronDown, FiChevronRight, FiRefreshCw } from 'react-icons/fi';

interface LogMeta {
  file: string;
  timestamp: string;
}

interface LogViewerProps {
  sessionId: string;
}

interface LogContent {
  session_id: string;
  sender: string;
  created_at: string;
  response_length: number;
  metadata: Record<string, unknown>;
  content: string;
}

export const LogViewer: React.FC<LogViewerProps> = ({ sessionId }) => {
  const [logs, setLogs] = useState<LogMeta[]>([]);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [contents, setContents] = useState<Record<string, LogContent | null>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadLogs = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.listLogs(sessionId);
      setLogs(data.logs || []);
    } catch (e) {
      const msg = (e as Error).message || 'Failed to load logs';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    if (sessionId) {
      void loadLogs();
    }
  }, [sessionId, loadLogs]);

  const toggleLog = async (file: string) => {
    const isOpen = expanded[file];
    if (!isOpen && !contents[file]) {
      try {
  const data = await apiService.getLog<LogContent>(sessionId, file);
  setContents(prev => ({ ...prev, [file]: data as LogContent }));
      } catch {
        setContents(prev => ({ ...prev, [file]: null }));
      }
    }
    setExpanded(prev => ({ ...prev, [file]: !isOpen }));
  };

  return (
    <div className="log-viewer-wrapper">
      <div className="log-viewer-header">
        <h3>LLM Response Logs</h3>
        <button onClick={loadLogs} className="refresh-button" disabled={loading}>
          <FiRefreshCw /> {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>
      {error && <div className="log-error">{error}</div>}
      <div className="log-list custom-scrollbar">
        {logs.length === 0 && !loading && <div className="empty">No logs yet for this session.</div>}
        {logs.map(l => {
          const isOpen = !!expanded[l.file];
          const content = contents[l.file];
          return (
            <div key={l.file} className="log-item">
              <button className="log-toggle" onClick={() => toggleLog(l.file)}>
                {isOpen ? <FiChevronDown /> : <FiChevronRight />}
                <FiFileText className="icon" />
                <span className="filename" title={l.file}>{l.file}</span>
                <span className="timestamp">{new Date(l.timestamp).toLocaleTimeString()}</span>
              </button>
              {isOpen && (
                <div className="log-content">
                  {content ? (
                    <pre className="raw-json">{JSON.stringify(content, null, 2)}</pre>
                  ) : (
                    <div className="loading">Loading...</div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
      <style>{`
        .log-viewer-wrapper { display: flex; flex-direction: column; height: 100%; }
        .log-viewer-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
        .log-viewer-header h3 { margin: 0; font-size: 1rem; }
        .refresh-button { display: inline-flex; align-items: center; gap: 4px; background: #1f2937; color: #e5e7eb; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; }
        .log-list { flex: 1; overflow-y: auto; border: 1px solid #374151; border-radius: 6px; padding: 4px; background: #111827; }
        .log-item { border-bottom: 1px solid #1f2937; }
        .log-item:last-child { border-bottom: none; }
        .log-toggle { width: 100%; display: flex; align-items: center; gap: 6px; background: none; border: none; color: #d1d5db; text-align: left; padding: 6px 4px; cursor: pointer; font-size: 0.75rem; }
        .log-toggle:hover { background: #1f2937; }
        .log-toggle .icon { opacity: 0.6; }
        .filename { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .timestamp { font-size: 0.65rem; color: #9ca3af; }
        .log-content { background: #1f2937; padding: 6px 8px; border-radius: 4px; margin: 0 4px 8px 24px; }
        .raw-json { font-family: monospace; font-size: 0.65rem; line-height: 1.1rem; max-height: 250px; overflow: auto; margin: 0; }
        .empty { padding: 12px; font-size: 0.8rem; color: #6b7280; text-align: center; }
        .loading { padding: 8px; font-size: 0.7rem; color: #9ca3af; }
        .log-error { color: #f87171; font-size: 0.75rem; margin-bottom: 0.5rem; }
      `}</style>
    </div>
  );
};
