/**
 * VSCodium Bridge for CodeLve
 * 
 * Manages communication between CodeLve and VSCodium
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const EventEmitter = require('events');

class CodiumBridge extends EventEmitter {
  constructor(ideLauncher) {
    super();
    this.ideLauncher = ideLauncher;
    this.isConnected = false;
    this.currentWorkspace = null;
    this.currentFile = null;
    this.pendingCommands = [];
  }

  /**
   * Initialize the VSCodium bridge
   * 
   * @returns {Promise<boolean>} True if initialized successfully
   */
  async initialize() {
    try {
      if (!this.ideLauncher) {
        throw new Error('IDE Launcher not provided');
      }
      
      // Check if IDE Launcher is initialized
      if (!this.ideLauncher.isInitialized) {
        throw new Error('IDE Launcher not initialized');
      }
      
      // Set up connection status
      this.isConnected = true;
      
      console.log('VSCodium bridge initialized successfully');
      return true;
    } catch (error) {
      console.error('Error initializing VSCodium bridge:', error);
      return false;
    }
  }

  /**
   * Open a workspace in VSCodium
   * 
   * @param {string} workspacePath Path to workspace
   * @returns {Promise<boolean>} True if opened successfully
   */
  async openWorkspace(workspacePath) {
    if (!this.isConnected) {
      console.error('VSCodium bridge not connected');
      return false;
    }
    
    try {
      // Validate workspace path
      if (!fs.existsSync(workspacePath)) {
        throw new Error(`Workspace path does not exist: ${workspacePath}`);
      }
      
      // Launch VSCodium with workspace
      const success = await this.ideLauncher.launchIDE(workspacePath);
      
      if (success) {
        this.currentWorkspace = workspacePath;
        this.emit('workspace-opened', workspacePath);
      }
      
      return success;
    } catch (error) {
      console.error('Error opening workspace:', error);
      return false;
    }
  }

  /**
   * Open a file in VSCodium
   * 
   * @param {string} filePath Path to file
   * @returns {Promise<boolean>} True if opened successfully
   */
  async openFile(filePath) {
    if (!this.isConnected) {
      console.error('VSCodium bridge not connected');
      return false;
    }
    
    try {
      // Validate file path
      if (!fs.existsSync(filePath)) {
        throw new Error(`File path does not exist: ${filePath}`);
      }
      
      // Open file in VSCodium
      const success = await this.ideLauncher.openFile(filePath);
      
      if (success) {
        this.currentFile = filePath;
        this.emit('file-opened', filePath);
      }
      
      return success;
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
      console.error('VSCodium bridge not connected');
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
      
      // Open the file in VSCodium
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
   * Run a VSCodium command
   * 
   * @param {string} command Command to run
   * @param {Array<string>} args Command arguments
   * @returns {Promise<boolean>} True if command executed successfully
   */
  async runCommand(command, args = []) {
    if (!this.isConnected) {
      // Queue command for when connection is established
      this.pendingCommands.push({ command, args });
      return false;
    }
    
    try {
      // For now, running commands is not directly supported
      // We'd need to implement VSCode extension integration for more complex commands
      console.log(`Command execution requested: ${command} ${args.join(' ')}`);
      return true;
    } catch (error) {
      console.error('Error running command:', error);
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
   * Disconnect the VSCodium bridge
   */
  disconnect() {
    this.isConnected = false;
    this.currentWorkspace = null;
    this.currentFile = null;
    this.emit('disconnected');
  }
}

module.exports = CodiumBridge;