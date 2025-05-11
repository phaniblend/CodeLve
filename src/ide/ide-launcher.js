/**
 * IDE Launcher for CodeLve
 * 
 * Handles launching and integrating with VSCodium
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn } = require('child_process');

class IDELauncher {
  constructor() {
    this.processManager = null;
    this.isInitialized = false;
    this.config = {
      extensionsDir: path.join(os.homedir(), '.codelve', 'extensions'),
      dataDir: path.join(os.homedir(), '.codelve', 'data'),
      configDir: path.join(os.homedir(), '.codelve', 'config')
    };
  }

  /**
   * Initialize the IDE launcher
   * 
   * @param {Object} processManager Process manager instance
   * @returns {Promise<boolean>} True if initialized successfully
   */
  async initialize(processManager) {
    try {
      console.log('Initializing IDE launcher...');
      
      this.processManager = processManager;
      
      // Ensure required directories exist
      this.ensureDirectories();
      
      // Verify VSCodium is available
      const idePathVerified = await this.verifyIDEPath();
      if (!idePathVerified) {
        console.error('VSCodium not found');
        return false;
      }
      
      this.isInitialized = true;
      console.log('IDE launcher initialized successfully');
      return true;
    } catch (error) {
      console.error('Error initializing IDE launcher:', error);
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
   * Verify the VSCodium executable path
   * 
   * @returns {Promise<boolean>} True if verified
   */
  async verifyIDEPath() {
    const idePath = this.getIDEPath();
    
    if (!idePath) {
      console.error('VSCodium executable not found');
      return false;
    }
    
    if (!fs.existsSync(idePath)) {
      console.error(`VSCodium path does not exist: ${idePath}`);
      return false;
    }
    
    console.log(`Verified VSCodium path: ${idePath}`);
    return true;
  }

  /**
   * Get the path to the VSCodium executable
   * 
   * @returns {string|null} Path to VSCodium executable or null if not found
   */
  getIDEPath() {
    const platform = os.platform();
    const isWindows = platform === 'win32';
    const isMac = platform === 'darwin';
    const isLinux = platform === 'linux';
    
    // First check bundled location
    const appDir = process.resourcesPath || __dirname;
    const bundledPath = path.join(appDir, 'vscodium', 
      isWindows ? 'VSCodium.exe' : isMac ? 'VSCodium.app/Contents/MacOS/VSCodium' : 'vscodium');
    
    if (fs.existsSync(bundledPath)) {
      return bundledPath;
    }
    
    // Check common installation locations
    if (isWindows) {
      const possiblePaths = [
        path.join(os.homedir(), 'AppData', 'Local', 'Programs', 'VSCodium', 'VSCodium.exe'),
        'C:\\Program Files\\VSCodium\\VSCodium.exe',
        'C:\\Program Files (x86)\\VSCodium\\VSCodium.exe'
      ];
      
      for (const p of possiblePaths) {
        if (fs.existsSync(p)) return p;
      }
    } else if (isMac) {
      const possiblePaths = [
        '/Applications/VSCodium.app/Contents/MacOS/VSCodium',
        path.join(os.homedir(), 'Applications', 'VSCodium.app', 'Contents', 'MacOS', 'VSCodium')
      ];
      
      for (const p of possiblePaths) {
        if (fs.existsSync(p)) return p;
      }
    } else if (isLinux) {
      const possiblePaths = [
        '/usr/bin/vscodium',
        '/usr/local/bin/vscodium',
        '/snap/bin/vscodium'
      ];
      
      for (const p of possiblePaths) {
        if (fs.existsSync(p)) return p;
      }
    }
    
    return null;
  }

  /**
   * Launch VSCodium with the specified workspace
   * 
   * @param {string} workspacePath Path to workspace
   * @returns {Promise<boolean>} True if launched successfully
   */
  async launchIDE(workspacePath) {
    if (!this.isInitialized || !this.processManager) {
      console.error('IDE launcher not initialized');
      return false;
    }
    
    const idePath = this.getIDEPath();
    if (!idePath) {
      console.error('VSCodium executable not found');
      return false;
    }
    
    // Prepare arguments
    const args = [
      '--extensions-dir', this.config.extensionsDir,
      '--user-data-dir', this.config.dataDir
    ];
    
    // Add workspace if provided
    if (workspacePath && fs.existsSync(workspacePath)) {
      args.push(workspacePath);
    }
    
    // Launch VSCodium through process manager
    return this.processManager.startProcess('vscodium', idePath, args, {
      detached: true,
      stdio: 'ignore'
    });
  }

  /**
   * Install a VSCodium extension
   * 
   * @param {string} extensionId Extension ID
   * @returns {Promise<boolean>} True if installed successfully
   */
  async installExtension(extensionId) {
    if (!this.isInitialized || !this.processManager) {
      console.error('IDE launcher not initialized');
      return false;
    }
    
    const idePath = this.getIDEPath();
    if (!idePath) {
      console.error('VSCodium executable not found');
      return false;
    }
    
    return new Promise((resolve) => {
      const process = spawn(idePath, ['--install-extension', extensionId]);
      
      process.stdout.on('data', (data) => {
        console.log(`Extension install: ${data.toString().trim()}`);
      });
      
      process.stderr.on('data', (data) => {
        console.error(`Extension install error: ${data.toString().trim()}`);
      });
      
      process.on('close', (code) => {
        if (code === 0) {
          console.log(`Extension installed successfully: ${extensionId}`);
          resolve(true);
        } else {
          console.error(`Failed to install extension: ${extensionId} (code: ${code})`);
          resolve(false);
        }
      });
    });
  }

  /**
   * Open a file in VSCodium
   * 
   * @param {string} filePath Path to file
   * @returns {Promise<boolean>} True if opened successfully
   */
  async openFile(filePath) {
    if (!this.isInitialized || !this.processManager) {
      console.error('IDE launcher not initialized');
      return false;
    }
    
    if (!fs.existsSync(filePath)) {
      console.error(`File does not exist: ${filePath}`);
      return false;
    }
    
    const idePath = this.getIDEPath();
    if (!idePath) {
      console.error('VSCodium executable not found');
      return false;
    }
    
    // Open file in VSCodium
    return this.processManager.startProcess('vscodium-file', idePath, [
      '--extensions-dir', this.config.extensionsDir,
      '--user-data-dir', this.config.dataDir,
      filePath
    ]);
  }
}

module.exports = IDELauncher;