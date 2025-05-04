const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const { spawn } = require('child_process');
const modelManager = require('./model-manager');
const Store = require('electron-store');

// Initialize store for app settings
const store = new Store({
  name: 'settings',
  defaults: {
    windowBounds: { width: 1200, height: 800 },
    isDarkMode: true,
    telemetryEnabled: false
  }
});

let mainWindow;
let serverProcess;

// Start the Express server
function startServer() {
  const serverPath = path.join(__dirname, '../server/index.js');
  
  // Use node to start the server
  serverProcess = spawn('node', [serverPath], {
    stdio: 'pipe' // Capture output for logging
  });
  
  serverProcess.stdout.on('data', (data) => {
    console.log(`Server: ${data}`);
  });
  
  serverProcess.stderr.on('data', (data) => {
    console.error(`Server error: ${data}`);
  });
  
  serverProcess.on('close', (code) => {
    console.log(`Server exited with code ${code}`);
  });
}

function createWindow() {
  const { width, height } = store.get('windowBounds');
  
  // Create the browser window
  mainWindow = new BrowserWindow({
    width,
    height,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load the app
  mainWindow.loadURL(
    isDev
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '../dist/index.html')}`
  );

  // Open DevTools in development mode
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  // Save window size when resized
  mainWindow.on('resize', () => {
    const { width, height } = mainWindow.getBounds();
    store.set('windowBounds', { width, height });
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Initialize app
app.on('ready', async () => {
  // Start backend server
  startServer();
  
  // Start Ollama if not running
  const ollamaStatus = await modelManager.checkOllamaStatus();
  if (!ollamaStatus.running) {
    console.log('Ollama not running, attempting to start...');
    await modelManager.startOllama();
  }
  
  // Create window
  createWindow();
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Clean up on app quit
app.on('quit', () => {
  // Kill the server process
  if (serverProcess) {
    serverProcess.kill();
  }
});

// IPC handlers
ipcMain.handle('get-settings', () => {
  return {
    isDarkMode: store.get('isDarkMode'),
    telemetryEnabled: store.get('telemetryEnabled')
  };
});

ipcMain.handle('save-settings', (event, settings) => {
  store.set(settings);
  return { success: true };
});

ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  
  if (result.canceled) {
    return { canceled: true };
  }
  
  return { path: result.filePaths[0] };
});

// Ollama related IPC handlers
ipcMain.handle('ollama-status', async () => {
  return await modelManager.checkOllamaStatus();
});

ipcMain.handle('get-models', async () => {
  return await modelManager.getInstalledModels();
});

ipcMain.handle('pull-model', async (event, modelName) => {
  return await modelManager.pullModel(modelName);
});

ipcMain.handle('set-default-model', (event, modelName) => {
  return modelManager.setDefaultModel(modelName);
});

ipcMain.handle('get-default-model', () => {
  return modelManager.getDefaultModel();
});

ipcMain.handle('save-model-settings', (event, modelName, settings) => {
  return modelManager.saveModelSettings(modelName, settings);
});

ipcMain.handle('get-model-settings', (event, modelName) => {
  return modelManager.getModelSettings(modelName);
});

ipcMain.handle('is-ollama-installed', async () => {
  return await modelManager.isOllamaInstalled();
});

ipcMain.handle('start-ollama', async () => {
  return await modelManager.startOllama();
});