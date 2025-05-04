import React, { createContext, useState, useEffect, useContext } from 'react';

// Create context
const AppContext = createContext();

// Provider component
export const AppProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(false);
  const [codebase, setCodebase] = useState(null);
  const [ollamaStatus, setOllamaStatus] = useState({
    running: false,
    checking: true,
    error: null
  });
  const [availableModels, setAvailableModels] = useState([]);
  const [settings, setSettings] = useState({
    model: 'mistral',
    temperatureValue: 0.7,
    maxContextLength: 4000,
    telemetryEnabled: false,
  });
  const [currentSession, setCurrentSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  
  // Check app settings on load
  useEffect(() => {
    const initializeSettings = async () => {
      if (window.api) {
        try {
          // Get app settings
          const appSettings = await window.api.getSettings();
          setDarkMode(appSettings.isDarkMode);
          
          // Check Ollama status
          checkOllamaStatus();
          
          // Load sessions
          loadSessions();
        } catch (error) {
          console.error('Error initializing settings:', error);
        }
      }
    };
    
    initializeSettings();
  }, []);
  
  // Check Ollama status
  const checkOllamaStatus = async () => {
    try {
      if (window.api) {
        setOllamaStatus({
          running: false,
          checking: true,
          error: null
        });
        
        const status = await window.api.ollamaStatus();
        
        setOllamaStatus({
          running: status.running,
          checking: false,
          error: status.error || null
        });
        
        if (status.running) {
          // Get available models
          loadAvailableModels();
        }
      }
    } catch (error) {
      setOllamaStatus({
        running: false,
        checking: false,
        error: error.message
      });
    }
  };
  
  // Load available models
  const loadAvailableModels = async () => {
    try {
      if (window.api) {
        const models = await window.api.getModels();
        setAvailableModels(models);
        
        // Get default model
        const defaultModel = await window.api.getDefaultModel();
        
        // Update settings with default model
        setSettings(prev => ({
          ...prev,
          model: defaultModel
        }));
      }
    } catch (error) {
      console.error('Error loading models:', error);
    }
  };
  
  // Load sessions
  const loadSessions = async () => {
    try {
      if (window.api) {
        const sessionsData = await window.api.getSessions();
        setSessions(sessionsData);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };
  
  // Toggle dark mode
  const toggleDarkMode = async () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    
    if (window.api) {
      try {
        await window.api.saveSettings({ isDarkMode: newMode });
      } catch (error) {
        console.error('Error saving dark mode setting:', error);
      }
    }
  };
  
  // Select codebase folder
  const selectCodebase = async () => {
    try {
      if (window.api) {
        const result = await window.api.selectFolder();
        if (!result.canceled) {
          const codebaseData = {
            path: result.path,
            name: result.path.split('\\').pop() || result.path.split('/').pop()
          };
          
          setCodebase(codebaseData);
          return codebaseData;
        }
      }
    } catch (error) {
      console.error('Error selecting codebase:', error);
    }
    return null;
  };
  
  // Save settings
  const saveSettings = async (newSettings) => {
    setSettings(newSettings);
    
    if (window.api) {
      try {
        // Save model specific settings
        await window.api.saveModelSettings(newSettings.model, {
          temperature: newSettings.temperatureValue,
          maxTokens: parseInt(newSettings.maxContextLength)
        });
        
        // Set as default model
        await window.api.setDefaultModel(newSettings.model);
        
        // Save telemetry setting
        await window.api.saveSettings({
          telemetryEnabled: newSettings.telemetryEnabled
        });
      } catch (error) {
        console.error('Error saving settings:', error);
      }
    }
  };
  
  // Create a new session
  const createSession = async (name = null) => {
    if (!codebase) return null;
    
    const sessionName = name || `${codebase.name} - ${new Date().toLocaleString()}`;
    
    try {
      if (window.api) {
        const session = await window.api.createSession(sessionName, codebase.path);
        
        // Reload sessions
        await loadSessions();
        
        // Set as current session
        setCurrentSession(session);
        
        return session;
      }
    } catch (error) {
      console.error('Error creating session:', error);
    }
    
    return null;
  };
  
  // Load a session
  const loadSession = async (sessionId) => {
    try {
      if (window.api) {
        const session = await window.api.getSession(sessionId);
        setCurrentSession(session);
        
        // Set codebase from session
        setCodebase({
          path: session.codebase_path,
          name: session.codebase_path.split('\\').pop() || session.codebase_path.split('/').pop()
        });
        
        return session;
      }
    } catch (error) {
      console.error('Error loading session:', error);
    }
    
    return null;
  };
  
  // Pull a model
  const pullModel = async (modelName) => {
    try {
      if (window.api) {
        const result = await window.api.pullModel(modelName);
        
        if (result.success) {
          // Reload available models
          await loadAvailableModels();
        }
        
        return result;
      }
    } catch (error) {
      console.error('Error pulling model:', error);
      return { success: false, error: error.message };
    }
  };
  
  // Start Ollama if not running
  const startOllama = async () => {
    try {
      if (window.api) {
        const result = await window.api.startOllama();
        
        if (result.success) {
          await checkOllamaStatus();
        }
        
        return result;
      }
    } catch (error) {
      console.error('Error starting Ollama:', error);
      return { success: false, error: error.message };
    }
  };

  return (
    <AppContext.Provider
      value={{
        darkMode,
        toggleDarkMode,
        codebase,
        selectCodebase,
        ollamaStatus,
        checkOllamaStatus,
        availableModels,
        settings,
        saveSettings,
        pullModel,
        startOllama,
        currentSession,
        sessions,
        createSession,
        loadSession,
        loadSessions
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

// Custom hook to use the AppContext
export const useApp = () => useContext(AppContext);

export default AppContext;