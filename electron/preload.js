const { contextBridge, ipcRenderer } = require('electron');
const axios = require('axios');

// API base URL
const API_BASE_URL = 'http://localhost:3001/api';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'api', {
    // App settings
    getSettings: async () => ipcRenderer.invoke('get-settings'),
    saveSettings: async (settings) => ipcRenderer.invoke('save-settings', settings),
    
    // File system operations
    selectFolder: async () => ipcRenderer.invoke('select-folder'),
    
    // Ollama integration
    ollamaStatus: async () => ipcRenderer.invoke('ollama-status'),
    getModels: async () => ipcRenderer.invoke('get-models'),
    pullModel: async (modelName) => ipcRenderer.invoke('pull-model', modelName),
    setDefaultModel: async (modelName) => ipcRenderer.invoke('set-default-model', modelName),
    getDefaultModel: async () => ipcRenderer.invoke('get-default-model'),
    saveModelSettings: async (modelName, settings) => ipcRenderer.invoke('save-model-settings', modelName, settings),
    getModelSettings: async (modelName) => ipcRenderer.invoke('get-model-settings', modelName),
    isOllamaInstalled: async () => ipcRenderer.invoke('is-ollama-installed'),
    startOllama: async () => ipcRenderer.invoke('start-ollama'),
    
    // Backend API calls via Express server
    getBackendStatus: async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/status`);
        return response.data;
      } catch (error) {
        console.error('Error getting status:', error);
        return { error: error.message };
      }
    },
    
    listDirectory: async (dirPath) => {
      try {
        const response = await axios.post(`${API_BASE_URL}/list-directory`, { path: dirPath });
        return response.data;
      } catch (error) {
        console.error('Error listing directory:', error);
        return { error: error.message };
      }
    },
    
    readFile: async (filePath) => {
      try {
        const response = await axios.post(`${API_BASE_URL}/read-file`, { path: filePath });
        return response.data;
      } catch (error) {
        console.error('Error reading file:', error);
        return { error: error.message };
      }
    },
    
    sendChatMessage: async (message, model, temperature, maxTokens, sessionId) => {
      try {
        const response = await axios.post(`${API_BASE_URL}/chat`, {
          prompt: message,
          model,
          temperature,
          maxTokens,
          sessionId
        });
        return response.data;
      } catch (error) {
        console.error('Error sending chat message:', error);
        return { error: error.message };
      }
    },
    
    analyzeCode: async (prompt, codebasePath, model, temperature, maxTokens, sessionId) => {
      try {
        const response = await axios.post(`${API_BASE_URL}/analyze`, {
          prompt,
          codebasePath,
          model,
          temperature,
          maxTokens,
          sessionId
        });
        return response.data;
      } catch (error) {
        console.error('Error analyzing code:', error);
        return { error: error.message };
      }
    },
    
    // Session management
    createSession: async (name, codebasePath) => {
      try {
        const response = await axios.post(`${API_BASE_URL}/sessions`, {
          name,
          codebasePath
        });
        return response.data;
      } catch (error) {
        console.error('Error creating session:', error);
        return { error: error.message };
      }
    },
    
    getSessions: async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/sessions`);
        return response.data;
      } catch (error) {
        console.error('Error getting sessions:', error);
        return { error: error.message };
      }
    },
    
    getSession: async (sessionId) => {
      try {
        const response = await axios.get(`${API_BASE_URL}/sessions/${sessionId}`);
        return response.data;
      } catch (error) {
        console.error('Error getting session:', error);
        return { error: error.message };
      }
    }
  }
);