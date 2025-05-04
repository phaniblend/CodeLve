import React, { useState, useRef, useEffect } from 'react';
import PromptInput from './PromptInput';
import ResponseDisplay from './ResponseDisplay';
import { useApp } from '../contexts/AppContext';
import { sendChatMessage, analyzeCode } from '../utils/api';

const ChatInterface = () => {
  const { codebase, settings, currentSession, ollamaStatus } = useApp();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Load messages from session
  useEffect(() => {
    if (currentSession && currentSession.messages) {
      setMessages(currentSession.messages.map(msg => ({
        id: msg.id,
        content: msg.content,
        sender: msg.sender,
        timestamp: msg.timestamp
      })));
    } else {
      setMessages([]);
    }
  }, [currentSession]);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle sending a new message
  const handleSendMessage = async (content) => {
    if (!content.trim() || loading) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      content,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      let response;
      
      // Use different API based on whether we're analyzing code or just chatting
      if (codebase && content.toLowerCase().includes('code') || content.toLowerCase().includes('analyze')) {
        // Analyze code
        const result = await analyzeCode(
          content,
          codebase.path,
          currentSession?.id,
          {
            model: settings.model,
            temperature: settings.temperatureValue,
            maxTokens: parseInt(settings.maxContextLength)
          }
        );
        response = result.response;
      } else {
        // Regular chat
        const result = await sendChatMessage(
          content,
          currentSession?.id,
          {
            model: settings.model,
            temperature: settings.temperatureValue,
            maxTokens: parseInt(settings.maxContextLength)
          }
        );
        response = result.response;
      }
      
      const botResponse = {
        id: Date.now() + 1,
        content: response,
        sender: 'bot',
        timestamp: new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, botResponse]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        content: `Error: ${error.message}`,
        sender: 'system',
        timestamp: new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-13.5rem)] card">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-12 w-12 mx-auto mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
              <p className="text-lg font-medium">No messages yet</p>
              {!codebase ? (
                <p className="mt-1">
                  Select a codebase in the Files tab to get started.
                </p>
              ) : !currentSession ? (
                <p className="mt-1">
                  Start a session in the Files tab to begin analyzing your code.
                </p>
              ) : !ollamaStatus.running ? (
                <p className="mt-1">
                  Ollama is not running. Please start it in the Settings tab.
                </p>
              ) : (
                <p className="mt-1">
                  Start a conversation about your codebase. Ask questions or request an analysis.
                </p>
              )}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-3xl rounded-lg px-4 py-2 ${
                  message.sender === 'user'
                    ? 'bg-primary-600 text-white'
                    : message.sender === 'system'
                    ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                }`}
              >
                <ResponseDisplay content={message.content} />
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t dark:border-gray-700">
        <PromptInput 
          onSendMessage={handleSendMessage} 
          loading={loading} 
          disabled={!codebase || !currentSession || !ollamaStatus.running}
        />
      </div>
    </div>
  );
};

export default ChatInterface;