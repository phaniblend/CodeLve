/**
 * CodeLve - Advanced Integrated Development Environment
 * Main entry point for the application
 */

// Core dependencies
const path = require('path');
const { app, BrowserWindow, ipcMain } = require('electron');
const isDev = require('electron-is-dev');

// Custom modules
const ProcessManager = require('./process-manager');
const IDELauncher = require('../ide/ide-launcher');
const OllamaService = require('../ai/ollama-service');

// Global references
let mainWindow = null;
const processManager = new ProcessManager();
let ollamaService = null;

/**
 * Create the main application window
 */
function createMainWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    title: 'CodeLve IDE',
    show: false // Don't show until ready
  });

  // Load the UI
  const startUrl = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../../build/index.html')}`;
    
  mainWindow.loadURL(startUrl);

  // Show when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.maximize();
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * Initialize application components
 */
async function initializeApp() {
  try {
    console.log('Starting CodeLve...');
    
    // Initialize Ollama service
    ollamaService = new OllamaService();
    const ollamaReady = await ollamaService.initialize();
    
    if (!ollamaReady) {
      console.error('Failed to initialize Ollama service');
      // Continue anyway, will show error in UI
    }
    
    // Initialize IDE components
    const ideLauncher = new IDELauncher();
    await ideLauncher.initialize();
    
    // Create main window
    createMainWindow();
    
    console.log('CodeLve started successfully');
  } catch (error) {
    console.error('Error initializing CodeLve:', error);
    app.quit();
  }
}

// Application lifecycle events
app.on('ready', initializeApp);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createMainWindow();
  }
});

// Clean up on quit
app.on('will-quit', async () => {
  // Shut down all managed processes
  await processManager.shutdownAll();
  
  // Cleanup Ollama service
  if (ollamaService) {
    await ollamaService.shutdown();
  }
});

// IPC handlers for renderer process
ipcMain.handle('get-ollama-status', async () => {
  if (!ollamaService) return { running: false, error: 'Service not initialized' };
  return ollamaService.getStatus();
});

ipcMain.handle('query-ai', async (event, { prompt, context }) => {
  if (!ollamaService) return { error: 'AI service not available' };
  return ollamaService.processQuery(prompt, context);
});