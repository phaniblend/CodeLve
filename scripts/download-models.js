/**
 * Model Download Script for CodeLve
 * 
 * This script downloads language models for use with llama.cpp
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const https = require('https');
const { spawn } = require('child_process');

// Define models directory
const modelsDir = path.join(os.homedir(), '.codelve', 'models');

// Ensure directory exists
if (!fs.existsSync(modelsDir)) {
  fs.mkdirSync(modelsDir, { recursive: true });
  console.log(`Created models directory at: ${modelsDir}`);
}

// Define available models
const availableModels = {
  'mistral': {
    url: 'https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q4_K_M.gguf',
    filename: 'mistral.gguf',
    description: 'Mistral 7B (4-bit quantized)',
    size: '4.1 GB'
  },
  'llama2': {
    url: 'https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf',
    filename: 'llama2.gguf',
    description: 'Llama-2 7B (4-bit quantized)',
    size: '3.8 GB'
  },
  'codegemma': {
    url: 'https://huggingface.co/bartowski/CodeGemma-7b-GGUF/resolve/main/codegemma-7b-instruct-q4_0.gguf',
    filename: 'codegemma.gguf',
    description: 'CodeGemma 7B Instruct (4-bit quantized)',
    size: '4.7 GB'
  }
};

/**
 * Download a file
 * 
 * @param {string} url URL to download
 * @param {string} outputPath Output file path
 * @returns {Promise<void>}
 */
function downloadFile(url, outputPath) {
  return new Promise((resolve, reject) => {
    console.log(`Starting download: ${path.basename(outputPath)}`);
    console.log(`Output path: ${outputPath}`);
    
    const file = fs.createWriteStream(outputPath);
    let receivedBytes = 0;
    let totalBytes = 0;
    
    https.get(url, response => {
      if (response.statusCode !== 200) {
        return reject(new Error(`Failed to download ${url}: ${response.statusCode} ${response.statusMessage}`));
      }
      
      totalBytes = parseInt(response.headers['content-length'], 10);
      
      response.on('data', chunk => {
        receivedBytes += chunk.length;
        file.write(chunk);
        
        const percent = Math.round((receivedBytes / totalBytes) * 100);
        const mbReceived = (receivedBytes / 1024 / 1024).toFixed(2);
        const mbTotal = (totalBytes / 1024 / 1024).toFixed(2);
        
        process.stdout.write(`\rDownloading: ${percent}% (${mbReceived} MB / ${mbTotal} MB)`);
      });
      
      response.on('end', () => {
        file.end();
        console.log(`\nDownload complete: ${path.basename(outputPath)}`);
        resolve();
      });
      
      response.on('error', err => {
        fs.unlink(outputPath, () => {}); // Delete the file if download fails
        reject(err);
      });
    }).on('error', err => {
      fs.unlink(outputPath, () => {}); // Delete the file if request fails
      reject(err);
    });
    
    file.on('error', err => {
      fs.unlink(outputPath, () => {}); // Delete the file if write fails
      reject(err);
    });
  });
}

/**
 * Download model using local tools
 * 
 * @param {string} url URL to download
 * @param {string} outputPath Output file path
 * @returns {Promise<boolean>} True if successful
 */
function downloadWithLocalTools(url, outputPath) {
  return new Promise((resolve, reject) => {
    // Check for available download tools
    const platform = os.platform();
    let downloadProcess;
    
    if (platform === 'win32') {
      // Use PowerShell on Windows
      console.log('Using PowerShell to download...');
      downloadProcess = spawn('powershell', [
        '-Command',
        `Write-Host "Downloading to ${outputPath}..."; Invoke-WebRequest -Uri "${url}" -OutFile "${outputPath}" -UseBasicParsing`
      ]);
    } else {
      // Use curl on macOS/Linux
      console.log('Using curl to download...');
      downloadProcess = spawn('curl', ['-L', url, '-o', outputPath, '--progress-bar']);
    }
    
    let stderr = '';
    
    downloadProcess.stdout.on('data', (data) => {
      process.stdout.write(data.toString());
    });
    
    downloadProcess.stderr.on('data', (data) => {
      stderr += data.toString();
      // curl uses stderr for progress output
      process.stdout.write(data.toString());
    });
    
    downloadProcess.on('close', (code) => {
      if (code === 0) {
        console.log('\nDownload complete.');
        resolve(true);
      } else {
        console.error(`\nDownload failed with code ${code}: ${stderr}`);
        resolve(false);
      }
    });
    
    downloadProcess.on('error', (err) => {
      console.error('Error executing download command:', err);
      resolve(false);
    });
  });
}

/**
 * Main function
 */
async function main() {
  // Parse command line arguments
  const modelName = process.argv[2]?.toLowerCase();
  
  if (!modelName || !availableModels[modelName]) {
    console.log('Available models:');
    Object.entries(availableModels).forEach(([name, info]) => {
      console.log(`  - ${name}: ${info.description} (${info.size})`);
    });
    console.log('\nUsage: npm run download-models <model-name>');
    process.exit(1);
  }
  
  const model = availableModels[modelName];
  const outputPath = path.join(modelsDir, model.filename);
  
  console.log(`Downloading ${model.description} (${model.size})...`);
  console.log(`Model will be saved to: ${outputPath}`);
  
  try {
    // First try using Node.js HTTPS
    try {
      await downloadFile(model.url, outputPath);
    } catch (error) {
      console.error(`Error downloading with Node.js HTTPS: ${error.message}`);
      console.log('Trying alternative download method...');
      
      // Try with local tools if Node.js HTTPS fails
      const success = await downloadWithLocalTools(model.url, outputPath);
      
      if (!success) {
        throw new Error('All download methods failed');
      }
    }
    
    console.log('Model download completed successfully!');
    console.log(`Model saved to: ${outputPath}`);
    console.log('\nYou can now use this model with CodeLve.');
  } catch (error) {
    console.error(`Failed to download model: ${error.message}`);
    process.exit(1);
  }
}

// Run the main function
main();