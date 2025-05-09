
// Core dependencies
const path = require('path');
const fs = require('fs');
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const isDev = require('electron-is-dev');
const Store = require('electron-store');

// Custom modules
const ProcessManager = require('./process-manager');
const IDELauncher = require('../ide/ide-launcher');
const CodiumBridge = require('../ide/codium-bridge');
const OllamaService = require('../ai/ollama-service');
const CodeContextProvider = require('../context/code-context-provider');

// Global references
let mainWindow = null;
const processManager = new ProcessManager();
let ollamaService = null;
let ideLauncher = null;
let codiumBridge = null;
let codeContextProvider = null;

// Settings store
const settings = new Store({
  name: 'codelve-settings',
  defaults: {
    theme: 'light',
    modelName: 'mistral',
    maxContextSize: 10000,
    windowSize: { width: 1200, height: 800 },
    isMaximized: false
  }
});

/**
 * Create the main application window
 */
function createMainWindow() {
  // Get stored window size
  const { width, height } = settings.get('windowSize');
  const isMaximized = settings.get('isMaximized');
  
  // Create the browser window
  mainWindow = new BrowserWindow({
    width,
    height,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    title: 'CodeLve IDE',
    show: false, // Don't show until ready
    frame: false // Frameless window for custom title bar
  });

 // Load the UI
const startUrl = `file://${path.join(__dirname, '../../index.html')}`;
  
mainWindow.loadURL(startUrl);

  // Show when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    if (isMaximized) {
      mainWindow.maximize();
    }
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
  
  // Save window size and position on close
  mainWindow.on('close', () => {
    if (!mainWindow.isMaximized()) {
      const { width, height } = mainWindow.getBounds();
      settings.set('windowSize', { width, height });
    }
    settings.set('isMaximized', mainWindow.isMaximized());
  });
  
  // Setup window control listeners
  setupWindowControls();
}

/**
 * Setup window control event listeners
 */
function setupWindowControls() {
  ipcMain.on('window-minimize', () => {
    if (mainWindow) mainWindow.minimize();
  });
  
  ipcMain.on('window-maximize', () => {
    if (mainWindow) {
      if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
      } else {
        mainWindow.maximize();
      }
    }
  });
  
  ipcMain.on('window-close', () => {
    if (mainWindow) mainWindow.close();
  });
}

/**
 * Initialize application components
 */
async function initializeApp() {
  try {
    console.log('Starting CodeLve...');
    
    // Initialize code context provider
    codeContextProvider = new CodeContextProvider();
    
    // Initialize Ollama service
    ollamaService = new OllamaService();
    ollamaService.modelName = settings.get('modelName');
    const ollamaReady = await ollamaService.initialize();
    
    if (!ollamaReady) {
      console.error('Failed to initialize Ollama service');
      // Continue anyway, will show error in UI
    }
    
    // Initialize IDE components
    ideLauncher = new IDELauncher();
    await ideLauncher.initialize(processManager);
    
    // Initialize VSCodium bridge
    codiumBridge = new CodiumBridge(ideLauncher);
    await codiumBridge.initialize();
    
    // Create main window
    createMainWindow();
    
    // Setup IPC handlers
    setupIPCHandlers();
    
    console.log('CodeLve started successfully');
  } catch (error) {
    console.error('Error initializing CodeLve:', error);
    app.quit();
  }
}

/**
 * Setup IPC handlers for renderer process
 */
function setupIPCHandlers() {
  // AI Service handlers
  ipcMain.handle('get-ollama-status', async () => {
    if (!ollamaService) return { running: false, error: 'Service not initialized' };
    return ollamaService.getStatus();
  });

  ipcMain.handle('query-ai', async (event, { prompt, context }) => {
    if (!ollamaService) return { error: 'AI service not available' };
    return ollamaService.processQuery(prompt, context);
  });
  
  // File system handlers
  ipcMain.handle('read-file', async (event, filePath) => {
    try {
      return fs.readFileSync(filePath, 'utf8');
    } catch (error) {
      console.error('Error reading file:', error);
      throw error;
    }
  });
  
  ipcMain.handle('write-file', async (event, filePath, content) => {
    try {
      fs.writeFileSync(filePath, content, 'utf8');
      return true;
    } catch (error) {
      console.error('Error writing file:', error);
      throw error;
    }
  });
  
  ipcMain.handle('list-directory', async (event, dirPath) => {
    try {
      return fs.readdirSync(dirPath, { withFileTypes: true }).map(dirent => ({
        name: dirent.name,
        isDirectory: dirent.isDirectory(),
        path: path.join(dirPath, dirent.name)
      }));
    } catch (error) {
      console.error('Error listing directory:', error);
      throw error;
    }
  });
  
  // IDE integration handlers
  ipcMain.handle('open-file', async (event, filePath) => {
    if (!codiumBridge) return { error: 'IDE bridge not available' };
    return codiumBridge.openFile(filePath);
  });
  
  ipcMain.handle('create-file', async (event, filePath, content) => {
    if (!codiumBridge) return { error: 'IDE bridge not available' };
    return codiumBridge.createFile(filePath, content);
  });
  
  // Dialog handlers
  ipcMain.handle('show-open-dialog', async (event, options) => {
    return dialog.showOpenDialog(mainWindow, options);
  });
  
  ipcMain.handle('show-save-dialog', async (event, options) => {
    return dialog.showSaveDialog(mainWindow, options);
  });
  
  // Settings handlers
  ipcMain.handle('get-settings', () => {
    return settings.store;
  });
  
  ipcMain.handle('save-settings', (event, newSettings) => {
    Object.keys(newSettings).forEach(key => {
      settings.set(key, newSettings[key]);
    });
    return settings.store;
  });
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
  
  // Disconnect VSCodium bridge
  if (codiumBridge) {
    codiumBridge.disconnect();
  }
});