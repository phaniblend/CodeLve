/**
 * Preload script for CodeLve
 * 
 * Establishes secure bridge between renderer process and main process
 * using Electron's contextBridge
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'api', {
    // Window controls
    minimizeWindow: () => ipcRenderer.send('window-minimize'),
    maximizeWindow: () => ipcRenderer.send('window-maximize'),
    closeWindow: () => ipcRenderer.send('window-close'),
    
    // External links
    openExternal: (url) => ipcRenderer.invoke('open-external', url),
    
    // AI Service methods
    getAIStatus: () => ipcRenderer.invoke('get-ai-status'), // New API name
    getOllamaStatus: () => ipcRenderer.invoke('get-ollama-status'), // Keep old name for compatibility
    queryAI: (params) => ipcRenderer.invoke('query-ai', params),
    
    // File system operations
    readFile: (path) => ipcRenderer.invoke('read-file', path),
    writeFile: (path, content) => ipcRenderer.invoke('write-file', path, content),
    listDirectory: (path) => ipcRenderer.invoke('list-directory', path),
    
    // Dialog operations
    showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
    showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
    
    // IDE integration methods
    openFile: (path) => ipcRenderer.invoke('open-file', path),
    createFile: (path, content) => ipcRenderer.invoke('create-file', path, content),
    
    // Settings methods
    getSettings: () => ipcRenderer.invoke('get-settings'),
    saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings)
  }
);

// Expose version information
contextBridge.exposeInMainWorld('appInfo', {
  version: '0.1.0', // Will be updated from package.json in production
  name: 'CodeLve'
});