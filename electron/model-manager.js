const { exec } = require('child_process');
const axios = require('axios');
const path = require('path');
const fs = require('fs');
const Store = require('electron-store');

// Initialize store for model data
const store = new Store({
  name: 'models',
  defaults: {
    installedModels: [],
    defaultModel: 'mistral',
    modelSettings: {}
  }
});

// Check if Ollama is running
async function checkOllamaStatus() {
  try {
    const response = await axios.get('http://localhost:11434/api/version');
    return { 
      running: true, 
      version: response.data.version 
    };
  } catch (error) {
    return { 
      running: false, 
      error: error.message 
    };
  }
}

// Get a list of available models from Ollama
async function getInstalledModels() {
  try {
    const response = await axios.get('http://localhost:11434/api/tags');
    const models = response.data.models || [];
    
    // Update store with installed models
    store.set('installedModels', models.map(model => model.name));
    
    return models;
  } catch (error) {
    console.error('Error getting Ollama models:', error);
    return [];
  }
}

// Pull a model from Ollama repository
async function pullModel(modelName) {
  return new Promise((resolve, reject) => {
    console.log(`Pulling model: ${modelName}`);
    
    // Use Ollama CLI to pull the model
    const ollamaProcess = exec(`ollama pull ${modelName}`, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error pulling model ${modelName}:`, error);
        return reject(error);
      }
      
      if (stderr) {
        console.error(`stderr: ${stderr}`);
      }
      
      console.log(`Model ${modelName} pulled successfully.`);
      
      // Update the installed models list
      getInstalledModels().catch(console.error);
      
      resolve({
        success: true,
        model: modelName
      });
    });
    
    // Stream the output to console
    ollamaProcess.stdout.on('data', (data) => {
      console.log(`${data}`);
    });
    
    ollamaProcess.stderr.on('data', (data) => {
      console.error(`${data}`);
    });
  });
}

// Set default model
function setDefaultModel(modelName) {
  store.set('defaultModel', modelName);
  return { success: true, defaultModel: modelName };
}

// Get default model
function getDefaultModel() {
  return store.get('defaultModel', 'mistral');
}

// Save model settings
function saveModelSettings(modelName, settings) {
  const modelSettings = store.get('modelSettings', {});
  modelSettings[modelName] = settings;
  store.set('modelSettings', modelSettings);
  return { success: true };
}

// Get model settings
function getModelSettings(modelName) {
  const modelSettings = store.get('modelSettings', {});
  return modelSettings[modelName] || {
    temperature: 0.7,
    maxTokens: 4000
  };
}

// Check if Ollama is installed
function isOllamaInstalled() {
  return new Promise((resolve) => {
    exec('ollama --version', (error) => {
      if (error) {
        resolve(false);
      } else {
        resolve(true);
      }
    });
  });
}

// Start Ollama if it's not running
async function startOllama() {
  try {
    const status = await checkOllamaStatus();
    if (status.running) {
      return { success: true, message: 'Ollama is already running' };
    }
    
    // Check if Ollama is installed
    const installed = await isOllamaInstalled();
    if (!installed) {
      return { 
        success: false, 
        error: 'Ollama is not installed on this system. Please install it from https://ollama.ai/download' 
      };
    }
    
    // Start Ollama
    return new Promise((resolve) => {
      const ollamaProcess = exec('ollama serve', (error) => {
        if (error) {
          console.error('Error starting Ollama:', error);
          resolve({ 
            success: false, 
            error: `Failed to start Ollama: ${error.message}` 
          });
        }
      });
      
      // Give it some time to start
      setTimeout(async () => {
        const newStatus = await checkOllamaStatus();
        if (newStatus.running) {
          resolve({ success: true, message: 'Ollama started successfully' });
        } else {
          resolve({ 
            success: false, 
            error: 'Failed to start Ollama after waiting' 
          });
        }
      }, 2000);
    });
  } catch (error) {
    console.error('Error in startOllama:', error);
    return { success: false, error: error.message };
  }
}

module.exports = {
  checkOllamaStatus,
  getInstalledModels,
  pullModel,
  setDefaultModel,
  getDefaultModel,
  saveModelSettings,
  getModelSettings,
  isOllamaInstalled,
  startOllama
};