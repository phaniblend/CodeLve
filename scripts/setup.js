/**
 * Setup Script for CodeLve
 * 
 * Helps install and configure dependencies for CodeLve
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { exec, spawn } = require('child_process');
const readline = require('readline');

// Create interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Configuration directories
const homeDir = os.homedir();
const configDir = path.join(homeDir, '.codelve');
const modelsDir = path.join(configDir, 'models');
const liteXLDir = path.join(configDir, 'lite-xl');
const pluginsDir = path.join(liteXLDir, 'plugins');
const configFiles = path.join(liteXLDir, 'config');

// Check for OS
const platform = os.platform();
const isWindows = platform === 'win32';
const isMac = platform === 'darwin';
const isLinux = platform === 'linux';

/**
 * Main setup function
 */
async function main() {
  console.log('\n=== CodeLve Setup ===\n');
  
  // Create configuration directories
  createDirectories();
  
  // Check for Node.js modules
  await checkNodeModules();
  
  // Check for Lite XL
  const liteXLInstalled = await checkLiteXL();
  
  if (!liteXLInstalled) {
    const installLiteXL = await askQuestion('Would you like to install Lite XL? (y/n): ');
    
    if (installLiteXL.toLowerCase() === 'y') {
      await installLiteXLEditor();
    } else {
      console.log('Skipping Lite XL installation.');
    }
  }
  
  // Check for language models
  const modelsAvailable = checkModels();
  
  if (!modelsAvailable) {
    const downloadModel = await askQuestion('Would you like to download a language model? (y/n): ');
    
    if (downloadModel.toLowerCase() === 'y') {
      await downloadLanguageModel();
    } else {
      console.log('Skipping language model download.');
    }
  }
  
  // Setup Lite XL plugins
  await setupLiteXLPlugins();
  
  console.log('\n=== Setup Complete ===\n');
  console.log('You can now run CodeLve with: npm start');
  
  rl.close();
}

/**
 * Create necessary directories
 */
function createDirectories() {
  console.log('Creating configuration directories...');
  
  const dirs = [
    configDir,
    modelsDir,
    liteXLDir,
    pluginsDir,
    configFiles
  ];
  
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log(`Created: ${dir}`);
    }
  }
  
  console.log('Configuration directories created.');
}

/**
 * Check Node.js modules
 */
async function checkNodeModules() {
  console.log('\nChecking Node.js dependencies...');
  
  if (!fs.existsSync('node_modules')) {
    console.log('Node modules not found. Installing dependencies...');
    
    return new Promise((resolve, reject) => {
      const npmInstall = spawn('npm', ['install']);
      
      npmInstall.stdout.on('data', (data) => {
        process.stdout.write(data.toString());
      });
      
      npmInstall.stderr.on('data', (data) => {
        process.stderr.write(data.toString());
      });
      
      npmInstall.on('close', (code) => {
        if (code === 0) {
          console.log('Dependencies installed successfully.');
          resolve();
        } else {
          console.error(`npm install failed with code ${code}`);
          reject(new Error('Failed to install dependencies'));
        }
      });
    });
  } else {
    console.log('Node.js dependencies already installed.');
  }
}

/**
 * Check if Lite XL is available
 */
async function checkLiteXL() {
  console.log('\nChecking for Lite XL editor...');
  
  const platform = os.platform();
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
      console.log(`Lite XL found at: ${p}`);
      return true;
    }
  }
  
  console.log('Lite XL not found.');
  return false;
}

/**
 * Install Lite XL editor
 */
async function installLiteXLEditor() {
  console.log('\nInstalling Lite XL editor...');
  
  let downloadUrl = '';
  let outputPath = '';
  
  // Define download URLs and paths based on platform
  if (isWindows) {
    downloadUrl = 'https://github.com/lite-xl/lite-xl/releases/download/v2.1.1/lite-xl-v2.1.1-Windows-x86_64.zip';
    outputPath = path.join(os.tmpdir(), 'lite-xl.zip');
  } else if (isMac) {
    downloadUrl = 'https://github.com/lite-xl/lite-xl/releases/download/v2.1.1/lite-xl-v2.1.1-macOS-x86_64.dmg';
    outputPath = path.join(os.tmpdir(), 'lite-xl.dmg');
  } else if (isLinux) {
    downloadUrl = 'https://github.com/lite-xl/lite-xl/releases/download/v2.1.1/lite-xl-v2.1.1-linux-x86_64.tar.gz';
    outputPath = path.join(os.tmpdir(), 'lite-xl.tar.gz');
  } else {
    console.error('Unsupported platform for automatic installation.');
    console.log('Please visit https://lite-xl.com/ to download and install manually.');
    return;
  }
  
  // Download Lite XL
  console.log(`Downloading Lite XL from: ${downloadUrl}`);
  console.log(`Saving to: ${outputPath}`);
  
  // Download and install based on platform
  if (isWindows) {
    // Download using PowerShell
    await execCommand(`powershell -Command "Invoke-WebRequest -Uri '${downloadUrl}' -OutFile '${outputPath}'"`);
    
    // Extract ZIP file
    const extractDir = path.join(os.tmpdir(), 'lite-xl-extract');
    
    if (!fs.existsSync(extractDir)) {
      fs.mkdirSync(extractDir, { recursive: true });
    }
    
    await execCommand(`powershell -Command "Expand-Archive -Path '${outputPath}' -DestinationPath '${extractDir}' -Force"`);
    
    // Copy to Program Files
    const installDir = path.join(process.env.LOCALAPPDATA, 'Programs', 'LiteXL');
    
    if (!fs.existsSync(installDir)) {
      fs.mkdirSync(installDir, { recursive: true });
    }
    
    // Copy files
    await execCommand(`powershell -Command "Copy-Item -Path '${extractDir}\\*' -Destination '${installDir}' -Recurse -Force"`);
    
    console.log(`Lite XL installed to: ${installDir}`);
  } else if (isMac) {
    // For macOS, download and mount DMG
    await execCommand(`curl -L "${downloadUrl}" -o "${outputPath}"`);
    
    console.log('Downloaded. Please follow the installation instructions to install Lite XL.');
    await execCommand(`open "${outputPath}"`);
  } else if (isLinux) {
    // For Linux, download and extract to /opt
    await execCommand(`curl -L "${downloadUrl}" -o "${outputPath}"`);
    
    // Extract to /opt
    await execCommand(`sudo mkdir -p /opt/lite-xl`);
    await execCommand(`sudo tar -xzf "${outputPath}" -C /opt/lite-xl --strip-components 1`);
    
    // Create symlink
    await execCommand(`sudo ln -sf /opt/lite-xl/lite-xl /usr/local/bin/lite-xl`);
    
    console.log('Lite XL installed to: /opt/lite-xl');
  }
  
  console.log('Lite XL installation completed.');
}

/**
 * Check for language models
 */
function checkModels() {
  console.log('\nChecking for language models...');
  
  const modelFiles = fs.readdirSync(modelsDir);
  const ggufModels = modelFiles.filter(file => file.endsWith('.gguf'));
  
  if (ggufModels.length > 0) {
    console.log('Found language models:');
    ggufModels.forEach(model => {
      console.log(`- ${model}`);
    });
    return true;
  } else {
    console.log('No language models found.');
    return false;
  }
}

/**
 * Download language model
 */
async function downloadLanguageModel() {
  console.log('\nDownloading language model...');
  
  console.log('Available models:');
  console.log('1. Mistral 7B (4-bit quantized, ~4.1 GB)');
  console.log('2. Llama-2 7B (4-bit quantized, ~3.8 GB)');
  console.log('3. CodeGemma 7B (4-bit quantized, ~4.7 GB)');
  
  const modelChoice = await askQuestion('Select a model (1-3): ');
  
  let modelName = '';
  
  switch (modelChoice) {
    case '1':
      modelName = 'mistral';
      break;
    case '2':
      modelName = 'llama2';
      break;
    case '3':
      modelName = 'codegemma';
      break;
    default:
      console.log('Invalid choice. Selecting Mistral 7B as default.');
      modelName = 'mistral';
  }
  
  // Execute the download script
  return new Promise((resolve, reject) => {
    const downloadScript = spawn('node', ['scripts/download-models.js', modelName]);
    
    downloadScript.stdout.on('data', (data) => {
      process.stdout.write(data.toString());
    });
    
    downloadScript.stderr.on('data', (data) => {
      process.stderr.write(data.toString());
    });
    
    downloadScript.on('close', (code) => {
      if (code === 0) {
        console.log('Language model downloaded successfully.');
        resolve();
      } else {
        console.error(`Model download failed with code ${code}`);
        reject(new Error('Failed to download language model'));
      }
    });
  });
}

/**
 * Setup Lite XL plugins
 */
async function setupLiteXLPlugins() {
  console.log('\nSetting up Lite XL plugins for CodeLve integration...');
  
  // Create CodeLve plugin directory
  const codelvePluginDir = path.join(pluginsDir, 'codelve');
  
  if (!fs.existsSync(codelvePluginDir)) {
    fs.mkdirSync(codelvePluginDir, { recursive: true });
  }
  
  // Create plugin file
  const pluginFile = path.join(codelvePluginDir, 'init.lua');
  const pluginContent = `-- CodeLve Plugin for Lite XL
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

local doc_save = core.save_doc
core.save_doc = function(doc, ...)
  local result = doc_save(doc, ...)
  if doc and doc.filename then
    notify_file_save(doc.filename)
  end
  return result
end

-- Add keymappings
keymap.add {
  ["ctrl+alt+c"] = "codelve:connect",
}

-- Apply CodeLve theme options
local style = require "core.style"
style.background = { common.color "#1e1e1e" }
style.background2 = { common.color "#252526" }
style.text = { common.color "#e9ecef" }
style.caret = { common.color "#0078d4" }
style.accent = { common.color "#0078d4" }
style.dim = { common.color "#6c757d" }
style.divider = { common.color "#333333" }

return {
  name = "CodeLve",
  version = "0.1",
  description = "Integration with CodeLve IDE",
  author = "CodeLve Team",
}`;

  fs.writeFileSync(pluginFile, pluginContent);
  console.log(`Created CodeLve plugin at: ${pluginFile}`);
  
  console.log('Lite XL plugin setup completed.');
}

/**
 * Execute a command and return result
 */
function execCommand(command) {
  return new Promise((resolve, reject) => {
    console.log(`Executing: ${command}`);
    
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error: ${error.message}`);
        reject(error);
        return;
      }
      
      if (stderr) {
        console.error(`stderr: ${stderr}`);
      }
      
      if (stdout) {
        console.log(`stdout: ${stdout}`);
      }
      
      resolve();
    });
  });
}

/**
 * Ask a question and get response
 */
function askQuestion(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
}

// Run the main function
main().catch(error => {
  console.error('Setup failed:', error);
  rl.close();
  process.exit(1);
});