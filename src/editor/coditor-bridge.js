/**
 * Lite XL Bridge for CodeLve
 * 
 * Manages communication between CodeLve and Lite XL editor
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const EventEmitter = require('events');
const os = require('os');

class coditor extends EventEmitter {
  constructor(processManager) {
    super();
    this.processManager = processManager;
    this.isConnected = false;
    this.currentWorkspace = null;
    this.currentFile = null;
    this.pendingCommands = [];
    this.config = {
      configDir: path.join(os.homedir(), '.codelve', 'lite-xl', 'config'),
      pluginsDir: path.join(os.homedir(), '.codelve', 'lite-xl', 'plugins'),
      userDir: path.join(os.homedir(), '.codelve', 'lite-xl', 'user')
    };
    this.ipcPort = 9877; // Port for IPC with Lite XL (will be implemented via plugin)
  }

  /**
   * Initialize the Lite XL bridge
   * 
   * @returns {Promise<boolean>} True if initialized successfully
   */
  async initialize() {
    try {
      if (!this.processManager) {
        throw new Error('Process manager not provided');
      }
      
      // Ensure required directories exist
      this.ensureDirectories();
      
      // Verify Lite XL is available
      const editorPathVerified = await this.verifyEditorPath();
      if (!editorPathVerified) {
        console.error('Lite XL not found');
        return false;
      }
      
      // Set up CodeLve plugin for Lite XL
      await this.setupPlugin();
      
      // Set up connection status
      this.isConnected = true;
      
      console.log('Lite XL bridge initialized successfully');
      return true;
    } catch (error) {
      console.error('Error initializing Lite XL bridge:', error);
      return false;
    }
  }

  /**
   * Ensure required directories exist
   */
  ensureDirectories() {
    for (const dir of Object.values(this.config)) {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        console.log(`Created directory: ${dir}`);
      }
    }
  }

  /**
   * Set up the CodeLve plugin for Lite XL
   * 
   * @returns {Promise<boolean>} True if setup successful
   */
  async setupPlugin() {
    try {
      const pluginDir = path.join(this.config.pluginsDir, 'codelve');
      
      // Create plugin directory if it doesn't exist
      if (!fs.existsSync(pluginDir)) {
        fs.mkdirSync(pluginDir, { recursive: true });
      }
      
      // Path to plugin file
      const pluginFile = path.join(pluginDir, 'init.lua');
      
      // Check if plugin already exists
      if (!fs.existsSync(pluginFile)) {
        // Create the plugin file with IPC capabilities
        const pluginContent = this.getPluginCode();
        fs.writeFileSync(pluginFile, pluginContent, 'utf8');
        console.log('Created CodeLve plugin for Lite XL');
      }
      
      return true;
    } catch (error) {
      console.error('Error setting up Lite XL plugin:', error);
      return false;
    }
  }

  /**
   * Get the Lua code for the CodeLve plugin
   * 
   * @returns {string} Lua plugin code
   */
  getPluginCode() {
    return `-- CodeLve Plugin for Lite XL
local core = require "core"
local command = require "core.command"
local keymap = require "core.keymap"

-- Communication with CodeLve
local function notify_file_open(filename)
  -- TODO: Implement IPC with Electron app
  print("CodeLve: File opened: " .. filename)
end

local function notify_file_save(filename)
  -- TODO: Implement IPC with Electron app
  print("CodeLve: File saved: " .. filename)
end

-- Register commands
command.add(nil, {
  ["codelve:connect"] = function()
    print("CodeLve: Connected to Lite XL")
  end,
})

-- Hook file operations
local doc_open = core.open_doc
core.open_doc = function(filename, ...)
  local doc = doc_open(filename, ...)
  if filename then
    notify_file_open(filename)
  end
  return doc
end

local doc_save = core.docs
core.docs = function(...)
  local doc = doc_save(...)
  if doc.filename then
    notify_file_save(doc.filename)
  end
  return doc
end

-- Add keymappings
keymap.add {
  ["ctrl+alt+c"] = "codelve:connect",
}

-- Apply CodeLve theme options
core.style.background = { common.color "#1e1e1e" }
core.style.background2 = { common.color "#252526" }
core.style.text = { common.color "#e9ecef" }
core.style.caret = { common.color "#0078d4" }
core.style.accent = { common.color "#0078d4" }
core.style.dim = { common.color "#6c757d" }
core.style.divider = { common.color "#333333" }

return {
  name = "CodeLve",
  version = "0.1",
  description = "Integration with CodeLve IDE",
  author = "CodeLve Team",
}
`;
  }

  /**
   * Verify the Lite XL executable path
   * 
   * @returns {Promise<boolean>} True if verified
   */
  async verifyEditorPath() {
    const editorPath = this.getEditorPath();
    
    if (!editorPath) {
      console.error('Lite XL executable not found');
      return false;
    }
    
    if (!fs.existsSync(editorPath)) {
      console.error(`Lite XL path does not exist: ${editorPath}`);
      return false;
    }
    
    console.log(`Verified Lite XL path: ${editorPath}`);
    return true;
  }

  /**
   * Get the path to the Lite XL executable
   * 
   * @returns {string|null} Path to Lite XL executable or null if not found
   */
  getEditorPath() {
    const platform = os.platform();
    const isWindows = platform === 'win32';
    const isMac = platform === 'darwin';
    const isLinux = platform === 'linux';
    
    // First check bundled location
    const appDir = process.resourcesPath || __dirname;
    const bundledPath = path.join(appDir, 'lite-xl', 
      isWindows ? 'lite-xl.exe' : isMac ? 'lite-xl.app/Contents/MacOS/lite-xl' : 'lite-xl');
    
    if (fs.existsSync(bundledPath)) {
      return bundledPath;
    }
    
    // Check common installation locations
    if (isWindows) {
      const possiblePaths = [
        path.join(os.homedir(), 'AppData', 'Local', 'Programs', 'LiteXL', 'lite-xl.exe'),
        'C:\\Program Files\\LiteXL\\lite-xl.exe',
        'C:\\Program Files (x86)\\LiteXL\\lite-xl.exe'
      ];
      
      for (const p of possiblePaths) {
        if (fs.existsSync(p)) return p;
      }
    } else if (isMac) {
      const possiblePaths = [
        '/Applications/LiteXL.app/Contents/MacOS/lite-xl',
        path.join(os.homedir(), 'Applications', 'LiteXL.app', 'Contents', 'MacOS', 'lite-xl')
      ];
      
      for (const p of possiblePaths) {
        if (fs.existsSync(p)) return p;
      }
    } else if (isLinux) {
      const possiblePaths = [
        '/usr/bin/lite-xl',
        '/usr/local/bin/lite-xl',
        '/opt/lite-xl/lite-xl'
      ];
      
      for (const p of possiblePaths) {
        if (fs.existsSync(p)) return p;
      }
    }
    
    return null;
  }

  /**
   * Launch Lite XL with the specified workspace
   * 
   * @param {string} workspacePath Path to workspace
   * @returns {Promise<boolean>} True if launched successfully
   */
  async launchEditor(workspacePath) {
    if (!this.isConnected || !this.processManager) {
      console.error('Lite XL bridge not connected');
      return false;
    }
    
    const editorPath = this.getEditorPath();
    if (!editorPath) {
      console.error('Lite XL executable not found');
      return false;
    }
    
    // Prepare arguments
    const args = [
      '--user-module-path', this.config.pluginsDir
    ];
    
    // Add workspace if provided
    if (workspacePath && fs.existsSync(workspacePath)) {
      if (fs.statSync(workspacePath).isDirectory()) {
        // If it's a directory, pass the directory for the project
        args.push('-p', workspacePath);
      } else {
        // If it's a file, just open the file
        args.push(workspacePath);
      }
    }
    
    // Launch Lite XL through process manager
    const success = await this.processManager.startProcess('lite-xl', editorPath, args, {
      detached: true,
      env: {
        ...process.env,
        LITE_USERDIR: this.config.userDir
      }
    });
    
    if (success) {
      this.currentWorkspace = workspacePath;
      this.emit('editor-launched', workspacePath);
    }
    
    return success;
  }

  /**
   * Open a file in Lite XL
   * 
   * @param {string} filePath Path to file
   * @returns {Promise<boolean>} True if opened successfully
   */
  async openFile(filePath) {
    if (!this.isConnected) {
      console.error('Lite XL bridge not connected');
      return false;
    }
    
    try {
      // Validate file path
      if (!fs.existsSync(filePath)) {
        throw new Error(`File path does not exist: ${filePath}`);
      }
      
      // If Lite XL is already running, we'll send a command to open the file
      // If not, launch Lite XL with the file
      const isRunning = this.processManager.isProcessRunning('lite-xl');
      
      if (isRunning) {
        // TODO: Implement IPC mechanism to tell running instance to open file
        console.log(`Lite XL is running, would send IPC to open: ${filePath}`);
        // For now, we'll just launch a new instance
        const success = await this.launchEditor(filePath);
        
        if (success) {
          this.currentFile = filePath;
          this.emit('file-opened', filePath);
        }
        
        return success;
      } else {
        // Launch Lite XL with the file
        const success = await this.launchEditor(filePath);
        
        if (success) {
          this.currentFile = filePath;
          this.emit('file-opened', filePath);
        }
        
        return success;
      }
    } catch (error) {
      console.error('Error opening file:', error);
      return false;
    }
  }

  /**
   * Create a new file with content
   * 
   * @param {string} filePath Path to file
   * @param {string} content File content
   * @returns {Promise<boolean>} True if created successfully
   */
  async createFile(filePath, content) {
    if (!this.isConnected) {
      console.error('Lite XL bridge not connected');
      return false;
    }
    
    try {
      // Ensure directory exists
      const directoryPath = path.dirname(filePath);
      if (!fs.existsSync(directoryPath)) {
        fs.mkdirSync(directoryPath, { recursive: true });
      }
      
      // Write file content
      fs.writeFileSync(filePath, content, 'utf8');
      
      // Open the file in Lite XL
      const success = await this.openFile(filePath);
      
      if (success) {
        this.emit('file-created', filePath);
      }
      
      return success;
    } catch (error) {
      console.error('Error creating file:', error);
      return false;
    }
  }

  /**
   * Get the current workspace path
   * 
   * @returns {string|null} Current workspace path or null if none
   */
  getCurrentWorkspace() {
    return this.currentWorkspace;
  }

  /**
   * Get the current file path
   * 
   * @returns {string|null} Current file path or null if none
   */
  getCurrentFile() {
    return this.currentFile;
  }

  /**
   * Disconnect the Lite XL bridge
   */
  disconnect() {
    this.isConnected = false;
    this.currentWorkspace = null;
    this.currentFile = null;
    this.emit('disconnected');
  }
}

module.exports = coditor;