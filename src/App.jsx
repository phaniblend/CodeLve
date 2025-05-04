import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import FileExplorer from './components/FileExplorer';
import Settings from './components/Settings';
import { useApp } from './contexts/AppContext';

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const { darkMode, toggleDarkMode } = useApp();

  // Handle tab switching
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? 'dark' : ''}`}>
      {/* App Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <img
                  className="h-8 w-auto"
                  src="/src/assets/logo.svg"
                  alt="CodeLve"
                />
                <span className="ml-2 text-xl font-bold text-primary-600 dark:text-primary-400">
                  CodeLve
                </span>
              </div>
            </div>
            <div className="flex items-center">
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-md text-gray-500 dark:text-gray-300 hover:text-gray-700 dark:hover:text-white"
              >
                {darkMode ? (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* App Tabs */}
      <div className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-4">
            <button
              className={`px-3 py-2 text-sm font-medium ${
                activeTab === 'chat'
                  ? 'border-b-2 border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
              }`}
              onClick={() => handleTabChange('chat')}
            >
              Chat
            </button>
            <button
              className={`px-3 py-2 text-sm font-medium ${
                activeTab === 'files'
                  ? 'border-b-2 border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
              }`}
              onClick={() => handleTabChange('files')}
            >
              Files
            </button>
            <button
              className={`px-3 py-2 text-sm font-medium ${
                activeTab === 'settings'
                  ? 'border-b-2 border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
              }`}
              onClick={() => handleTabChange('settings')}
            >
              Settings
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'files' && <FileExplorer />}
          {activeTab === 'settings' && <Settings />}
        </div>
      </main>

      {/* App Footer */}
      <footer className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
            CodeLve Desktop v0.1.0
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;