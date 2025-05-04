import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';

const FileExplorer = () => {
  const { codebase, selectCodebase, createSession, currentSession, sessions, loadSession } = useApp();
  const [fileTree, setFileTree] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSessions, setShowSessions] = useState(false);

  // Load file tree when codebase changes
  useEffect(() => {
    if (codebase && window.api) {
      loadFileTree(codebase.path);
    }
  }, [codebase]);

  const loadFileTree = async (dirPath) => {
    setLoading(true);
    setError(null);
    try {
      const result = await window.api.listDirectory({ path: dirPath });
      if (result.error) {
        throw new Error(result.error);
      }
      
      setFileTree({
        name: dirPath.split('\\').pop() || dirPath.split('/').pop(),
        type: 'directory',
        path: dirPath,
        children: result.files.map(file => ({
          name: file.name,
          type: file.isDirectory ? 'directory' : 'file',
          path: file.path,
          language: file.language
        }))
      });
    } catch (err) {
      console.error('Error loading file tree:', err);
      setError(`Failed to load files: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectFolder = async () => {
    setLoading(true);
    try {
      await selectCodebase();
    } catch (err) {
      setError('Failed to select folder. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSession = async () => {
    if (!codebase) return;
    
    try {
      const session = await createSession();
      if (session) {
        // Session created successfully
      }
    } catch (err) {
      setError('Failed to create session. Please try again.');
    }
  };

  const handleLoadSession = async (sessionId) => {
    try {
      await loadSession(sessionId);
      setShowSessions(false);
    } catch (err) {
      setError('Failed to load session. Please try again.');
    }
  };

  const renderFileTree = (node, level = 0) => {
    if (!node) return null;

    const indent = level * 20;

    if (node.type === 'file') {
      return (
        <div
          key={node.path}
          className="py-1 flex items-center hover:bg-gray-100 dark:hover:bg-gray-800 rounded px-2"
          style={{ paddingLeft: `${indent}px` }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4 text-gray-500 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
            />
          </svg>
          <span className="text-sm">{node.name}</span>
        </div>
      );
    }

    return (
      <React.Fragment key={node.path}>
        <div
          className="py-1 flex items-center hover:bg-gray-100 dark:hover:bg-gray-800 rounded px-2 font-medium"
          style={{ paddingLeft: `${indent}px` }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4 text-yellow-500 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
            />
          </svg>
          <span className="text-sm">{node.name}</span>
        </div>
        {node.children && node.children.map(child => renderFileTree(child, level + 1))}
      </React.Fragment>
    );
  };

  return (
    <div className="card h-[calc(100vh-13.5rem)]">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-medium">File Explorer</h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowSessions(!showSessions)}
            className="btn-secondary text-sm"
          >
            Sessions
          </button>
          <button
            onClick={handleSelectFolder}
            disabled={loading}
            className={`btn-primary text-sm ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {loading ? 'Selecting...' : 'Select Folder'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 p-3 rounded-md mb-4">
          {error}
        </div>
      )}

      {showSessions && (
        <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-md mb-4">
          <h3 className="text-sm font-medium mb-2">Sessions</h3>
          {sessions.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">No sessions found</p>
          ) : (
            <div className="max-h-40 overflow-y-auto">
              {sessions.map(session => (
                <div 
                  key={session.id}
                  className="py-2 px-3 hover:bg-gray-200 dark:hover:bg-gray-700 cursor-pointer rounded-md mb-1 flex justify-between items-center"
                  onClick={() => handleLoadSession(session.id)}
                >
                  <div>
                    <div className="text-sm font-medium">{session.name}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(session.created_at).toLocaleString()}
                    </div>
                  </div>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {codebase ? (
        <div>
          <div className="bg-gray-100 dark:bg-gray-800 p-2 rounded-md mb-4 overflow-x-auto flex justify-between items-center">
            <code className="text-sm">{codebase.path}</code>
            {!currentSession && (
              <button
                onClick={handleCreateSession}
                className="btn-secondary text-xs ml-2"
              >
                Start Session
              </button>
            )}
          </div>
          <div className="overflow-y-auto max-h-[calc(100vh-20rem)]">
            {fileTree && renderFileTree(fileTree)}
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center h-64 border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg">
          <div className="text-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-12 w-12 mx-auto text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
              />
            </svg>
            <p className="mt-2 text-gray-500 dark:text-gray-400">
              No folder selected. Click the button above to select a codebase folder.
            </p>
          </div>
        </div>
      )}
      
      {currentSession && (
        <div className="mt-4 bg-blue-100 dark:bg-blue-900 p-2 rounded-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
                Active Session: {currentSession.name}
              </p>
              <p className="text-xs text-blue-600 dark:text-blue-300">
                Created: {new Date(currentSession.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileExplorer;