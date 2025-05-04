import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';

const Settings = () => {
  const { 
    settings, 
    saveSettings, 
    ollamaStatus, 
    availableModels,
    pullModel,
    startOllama,
    checkOllamaStatus
  } = useApp();
  
  const [localSettings, setLocalSettings] = useState(settings);
  const [modelInput, setModelInput] = useState('');
  const [isPulling, setIsPulling] = useState(false);
  const [pullStatus, setPullStatus] = useState(null);
  const [isStartingOllama, setIsStartingOllama] = useState(false);

  useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setLocalSettings({
      ...localSettings,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSave = () => {
    saveSettings(localSettings);
    alert('Settings saved successfully!');
  };

  const handlePullModel = async () => {
    if (!modelInput.trim()) return;
    
    setIsPulling(true);
    setPullStatus({ message: `Pulling model: ${modelInput}...` });
    
    try {
      const result = await pullModel(modelInput);
      
      if (result.success) {
        setPullStatus({ success: true, message: `Model ${modelInput} pulled successfully.` });
        setModelInput('');
      } else {
        setPullStatus({ success: false, error: result.error });
      }
    } catch (error) {
      setPullStatus({ success: false, error: error.message });
    } finally {
      setIsPulling(false);
    }
  };

  const handleStartOllama = async () => {
    setIsStartingOllama(true);
    
    try {
      const result = await startOllama();
      
      if (result.success) {
        // Ollama started successfully
      } else {
        alert(`Failed to start Ollama: ${result.error}`);
      }
    } catch (error) {
      alert(`Error starting Ollama: ${error.message}`);
    } finally {
      setIsStartingOllama(false);
    }
  };

  const handleRefreshStatus = () => {
    checkOllamaStatus();
  };

  return (
    <div className="card">
      <h2 className="text-lg font-medium mb-6">Settings</h2>

      <div className="space-y-6">
        {/* Model Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            LLM Model
          </label>
          <select
            name="model"
            value={localSettings.model}
            onChange={handleChange}
            className="input"
          >
            {availableModels.length > 0 ? (
              availableModels.map((model) => (
                <option key={model.name} value={model.name}>
                  {model.name}
                </option>
              ))
            ) : (
              <>
                <option value="mistral">Mistral (Recommended)</option>
                <option value="llama3">Llama 3</option>
                <option value="codellama">Code Llama</option>
              </>
            )}
          </select>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Select which model to use for code analysis
          </p>
        </div>

        {/* Pull Model */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Pull New Model
          </label>
          <div className="flex">
            <input
              type="text"
              value={modelInput}
              onChange={(e) => setModelInput(e.target.value)}
              placeholder="e.g., mistral, llama3"
              className="input rounded-r-none"
              disabled={isPulling || !ollamaStatus.running}
            />
            <button
              onClick={handlePullModel}
              disabled={isPulling || !modelInput.trim() || !ollamaStatus.running}
              className={`btn-primary rounded-l-none ${
                isPulling || !modelInput.trim() || !ollamaStatus.running
                  ? 'opacity-50 cursor-not-allowed'
                  : ''
              }`}
            >
              {isPulling ? 'Pulling...' : 'Pull'}
            </button>
          </div>
          {pullStatus && (
            <p
              className={`mt-2 text-sm ${
                pullStatus.success === true
                  ? 'text-green-600 dark:text-green-400'
                  : pullStatus.success === false
                  ? 'text-red-600 dark:text-red-400'
                  : 'text-gray-500 dark:text-gray-400'
              }`}
            >
              {pullStatus.message || pullStatus.error}
            </p>
          )}
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Download additional models from Ollama
          </p>
        </div>

        {/* Temperature */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Temperature: {localSettings.temperatureValue}
          </label>
          <input
            type="range"
            name="temperatureValue"
            min="0"
            max="1"
            step="0.1"
            value={localSettings.temperatureValue}
            onChange={handleChange}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          />
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>More Deterministic</span>
            <span>More Creative</span>
          </div>
        </div>

        {/* Max Context Length */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Max Context Length
          </label>
          <select
            name="maxContextLength"
            value={localSettings.maxContextLength}
            onChange={handleChange}
            className="input"
          >
            <option value="2000">2,000 tokens</option>
            <option value="4000">4,000 tokens</option>
            <option value="8000">8,000 tokens</option>
            <option value="16000">16,000 tokens</option>
          </select>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Higher values allow for more context but require more memory
          </p>
        </div>

        {/* Telemetry */}
        <div className="flex items-start">
          <div className="flex items-center h-5">
            <input
              id="telemetryEnabled"
              name="telemetryEnabled"
              type="checkbox"
              checked={localSettings.telemetryEnabled}
              onChange={handleChange}
              className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded dark:bg-gray-700 dark:border-gray-600"
            />
          </div>
          <div className="ml-3 text-sm">
            <label
              htmlFor="telemetryEnabled"
              className="font-medium text-gray-700 dark:text-gray-300"
            >
              Enable telemetry
            </label>
            <p className="text-gray-500 dark:text-gray-400">
              Help improve CodeLve by sending anonymous usage data. No code or prompts are shared.
            </p>
          </div>
        </div>

        {/* Ollama Status */}
        <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-md">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Ollama Status
            </h3>
            <button
              onClick={handleRefreshStatus}
              className="text-primary-600 dark:text-primary-400 text-sm hover:underline"
            >
              Refresh
            </button>
          </div>
          <div className="flex items-center mb-2">
            {ollamaStatus.checking ? (
              <div className="flex items-center">
                <svg className="animate-spin h-4 w-4 mr-2 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Checking Ollama status...
                </span>
              </div>
            ) : ollamaStatus.running ? (
              <>
                <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Running on http://localhost:11434
                </span>
              </>
            ) : (
              <>
                <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Ollama is not running
                </span>
              </>
            )}
          </div>
          {ollamaStatus.error && (
            <div className="text-sm text-red-500 dark:text-red-400 mb-2">
              Error: {ollamaStatus.error}
            </div>
          )}
          {ollamaStatus.running && (
            <div className="text-sm text-gray-500 dark:text-gray-400">
              <p>Installed models: {availableModels.length > 0 
                ? availableModels.map(m => m.name).join(', ') 
                : 'Loading...'}</p>
            </div>
          )}
          {!ollamaStatus.running && !ollamaStatus.checking && (
            <div className="mt-2">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                Please install and start Ollama to use CodeLve.
              </p>
              <div className="flex space-x-2">
                <a 
                  href="https://ollama.ai/download" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary-600 dark:text-primary-400 text-sm hover:underline"
                >
                  Download Ollama
                </a>
                <button
                  onClick={handleStartOllama}
                  disabled={isStartingOllama}
                  className="text-primary-600 dark:text-primary-400 text-sm hover:underline"
                >
                  {isStartingOllama ? 'Starting...' : 'Start Ollama'}
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="pt-4">
          <button 
            onClick={handleSave}
            className="btn-primary"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;