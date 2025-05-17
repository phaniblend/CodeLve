/**
 * Run Script for CodeLve
 * 
 * Launches all components of CodeLve (Electron app, Lite XL, llama.cpp)
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Configuration
const homeDir = os.homedir();
const configDir = path.join(homeDir, '.codelve');
const modelsDir = path.join(configDir, 'models');

// Platform detection
const platform = os.platform();
const isWindows = platform === 'win32';
const isMac = platform === 'darwin';
const isLinux = platform === 'linux';

// Process references
let electronProcess = null;
let editorProcess = null;

/**
 * Main function
 */
async function main() {
  console.log('\n=== Starting CodeLve ===\n');
  
  // Check prerequisites
  checkPrerequisites();
  
  // Start application
  await startApplication();
  
  // Handle termination
  setupTerminationHandlers();
  
  console.log('\nCodeLve has started successfully.');
  console.log('Press Ctrl+C to exit.');
}

/**
 * Check prerequisites
 */
function checkPrerequisites() {
  console.log('Checking prerequisites...');
  
  // Check for configuration directory
  if (!fs.existsSync(configDir)) {
    console.log(`Creating configuration directory: ${configDir}`);
    fs.mkdirSync(configDir, { recursive: true });
  }
  
  // Check for models directory
  if (!fs.existsSync(modelsDir)) {
    console.log(`Creating models directory: ${modelsDir}`);
    fs.mkdirSync(modelsDir, { recursive: true });
  }
  
  // Check for language models
  const modelFiles = fs.readdirSync(modelsDir);
  const ggufModels = modelFiles.filter(file => file.endsWith('.gguf'));
  
  if (ggufModels.length === 0) {
    console.warn('WARNING: No language models found in models directory.');
    console.warn('The AI functionality may not work properly.');
    console.warn('Run "node scripts/download-models.js" to download language models.');
  } else {
    console.log(`Found ${ggufModels.length} language model(s).`);
  }
  
  // Check for Lite XL
  const liteXLPath = findLiteXL();
  
  if (!liteXLPath) {
    console.warn('WARNING: Lite XL not found. The editor integration will not work.');
    console.warn('Run "node scripts/setup.js" to install Lite XL.');
  } else {
    console.log(`Found Lite XL at: ${liteXLPath}`);
  }
  
  // Check for Node modules
  if (!fs.existsSync('node_modules')) {
    console.error('ERROR: Node modules not found. Please run "npm install" first.');
    process.exit(1);
  }
  
  console.log('Prerequisites check completed.');
}

/**
 * Find Lite XL executable
 */
function findLiteXL() {
  const possiblePaths = [];
  
  if (isWindows) {
    possiblePaths.push(
      path.join(os.homedir(), 'AppData', 'Local', 'Programs', 'LiteXL', 'lite-xl.exe'),
      'C:\\Program Files\\LiteXL\\lite-xl.exe',
      'C:\\Program Files (x86)\\LiteXL\\lite-xl.exe'
    );
  } else if (isMac) {
    possiblePaths.push(
      '/Applications/LiteXL.app/Contents/MacOS/lite-xl',
      path.join(os.homedir(), 'Applications', 'LiteXL.app', 'Contents', 'MacOS', 'lite-xl')
    );
  } else if (isLinux) {
    possiblePaths.push(
      '/usr/bin/lite-xl',
      '/usr/local/bin/lite-xl',
      '/opt/lite-xl/lite-xl'
    );
  }
  
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  
  return null;
}

/**
 * Start the application
 */
async function startApplication() {
  console.log('Starting application components...');
  
  // Start Electron app
  await startElectronApp();
  
  // Start Lite XL editor
  await startLiteXL();
  
  console.log('All components started.');
}

/**
 * Start the Electron app
 */
function startElectronApp() {
  return new Promise((resolve) => {
    console.log('Starting Electron app...');
    
    electronProcess = spawn('npm', ['start'], {
      stdio: 'inherit',
      shell: true
    });
    
    electronProcess.on('error', (error) => {
      console.error('Failed to start Electron app:', error);
    });
    
    // Give some time for Electron to start
    setTimeout(resolve, 2000);
  });
}

/**
 * Start Lite XL editor
 */
function startLiteXL() {
  return new Promise((resolve) => {
    const liteXLPath = findLiteXL();
    
    if (!liteXLPath) {
      console.warn('Skipping Lite XL launch as executable was not found.');
      resolve();
      return;
    }
    
    console.log('Starting Lite XL editor...');
    
    // Arguments for Lite XL
    const args = [
      '--user-module-path', path.join(configDir, 'lite-xl', 'plugins')
    ];
    
    editorProcess = spawn(liteXLPath, args, {
      env: {
        ...process.env,
        LITE_USERDIR: path.join(configDir, 'lite-xl', 'user')
      },
      detached: true,
      stdio: 'ignore'
    });
    
    editorProcess.on('error', (error) => {
      console.error('Failed to start Lite XL:', error);
    });
    
    // Allow the editor to run independently
    editorProcess.unref();
    
    // Give some time for Lite XL to start
    setTimeout(resolve, 1000);
  });
}

/**
 * Setup termination handlers
 */
function setupTerminationHandlers() {
  // Handle Ctrl+C
  process.on('SIGINT', cleanupAndExit);
  
  // Handle termination
  process.on('SIGTERM', cleanupAndExit);
  
  // Handle process exit
  process.on('exit', () => {
    cleanupAndExit();
  });
  
  // Handle uncaught exceptions
  process.on('uncaughtException', (error) => {
    console.error('Uncaught exception:', error);
    cleanupAndExit(1);
  });
}

/**
 * Cleanup resources and exit
 */
function cleanupAndExit(code = 0) {
  console.log('\nShutting down CodeLve...');
  
  if (electronProcess) {
    console.log('Terminating Electron app...');
    if (isWindows) {
      spawn('taskkill', ['/pid', electronProcess.pid, '/f', '/t']);
    } else {
      electronProcess.kill('SIGTERM');
    }
  }
  
  // We don't kill Lite XL since it might have unsaved changes
  // The user should close it manually
  
  console.log('Shutdown complete. Goodbye!');
  process.exit(code);
}

// Run the main function
main().catch(error => {
  console.error('Error starting CodeLve:', error);
  process.exit(1);
});