/**
 * Ollama Service for CodeLve
 * 
 * Manages communication with local Ollama server for AI functionality
 */

const axios = require('axios');
const { exec } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

class OllamaService {
  constructor() {
    this.serverUrl = 'http://localhost:11434';
    this.modelName = 'mistral';
    this.isReady = false;
    this.lastError = null;
    this.maxRetries = 3;
    this.isStartingServer = false;
  }

  /**
   * Initialize the Ollama service
   * 
   * @returns {Promise<boolean>} True if initialized successfully
   */
  async initialize() {
    try {
      console.log('Initializing Ollama service...');
      
      // Check if Ollama is running
      const isRunning = await this.checkServerRunning();
      
      if (!isRunning) {
        console.log('Ollama server not running, attempting to start...');
        const started = await this.startOllamaServer();
        if (!started) {
          this.lastError = 'Failed to start Ollama server';
          return false;
        }
      }
      
      // Check if model is available
      const modelAvailable = await this.checkModelAvailable();
      
      if (!modelAvailable) {
        console.log(`Model ${this.modelName} not available, attempting to download...`);
        const downloaded = await this.downloadModel();
        if (!downloaded) {
          this.lastError = `Failed to download model ${this.modelName}`;
          return false;
        }
      }
      
      this.isReady = true;
      console.log('Ollama service initialized successfully');
      return true;
    } catch (error) {
      this.lastError = `Error initializing Ollama: ${error.message}`;
      console.error(this.lastError);
      return false;
    }
  }

  /**
   * Check if Ollama server is running
   * 
   * @returns {Promise<boolean>} True if running
   */
  async checkServerRunning() {
    try {
      const response = await axios.get(`${this.serverUrl}/api/version`, { timeout: 2000 });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }

  /**
   * Start the Ollama server
   * 
   * @returns {Promise<boolean>} True if started successfully
   */
  async startOllamaServer() {
    if (this.isStartingServer) {
      console.log('Ollama server start already in progress...');
      
      // Wait for it to complete
      for (let i = 0; i < 30; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        const running = await this.checkServerRunning();
        if (running) return true;
      }
      
      return false;
    }
    
    this.isStartingServer = true;
    
    return new Promise((resolve) => {
      // Find Ollama executable
      const ollamaPath = this.getOllamaPath();
      
      if (!ollamaPath) {
        console.error('Ollama executable not found');
        this.isStartingServer = false;
        resolve(false);
        return;
      }
      
      console.log(`Starting Ollama server from: ${ollamaPath}`);
      
      // Execute Ollama serve command
      const ollamaProcess = exec(`"${ollamaPath}" serve`, (error) => {
        if (error) {
          console.error('Error starting Ollama server:', error);
          this.isStartingServer = false;
          resolve(false);
        }
      });
      
      // Wait for server to start
      let checkCount = 0;
      const checkInterval = setInterval(async () => {
        checkCount++;
        const running = await this.checkServerRunning();
        
        if (running) {
          clearInterval(checkInterval);
          this.isStartingServer = false;
          resolve(true);
        } else if (checkCount >= 30) {
          // Timeout after 30 seconds
          clearInterval(checkInterval);
          console.error('Timeout waiting for Ollama server to start');
          this.isStartingServer = false;
          resolve(false);
        }
      }, 1000);
    });
  }

  /**
   * Get the path to the Ollama executable
   * 
   * @returns {string|null} Path to Ollama executable or null if not found
   */
  getOllamaPath() {
    const platform = os.platform();
    const isWindows = platform === 'win32';
    const isMac = platform === 'darwin';
    const isLinux = platform === 'linux';
    
    // First check bundled location
    const appDir = process.resourcesPath || __dirname;
    const bundledPath = path.join(appDir, 'ollama', 
      isWindows ? 'ollama.exe' : 'ollama');
    
    if (fs.existsSync(bundledPath)) {
      return bundledPath;
    }
    
    // Check common installation locations
    if (isWindows) {
      const possiblePaths = [
        path.join(os.homedir(), 'AppData', 'Local', 'Programs', 'Ollama', 'ollama.exe'),
        'C:\\Program Files\\Ollama\\ollama.exe',
        'C:\\Program Files (x86)\\Ollama\\ollama.exe'
      ];
      
      for (const p of possiblePaths) {
        if (fs.existsSync(p)) return p;
      }
    } else if (isMac) {
      const possiblePaths = [
        '/Applications/Ollama.app/Contents/MacOS/Ollama',
        path.join(os.homedir(), 'Applications', 'Ollama.app', 'Contents', 'MacOS', 'Ollama')
      ];
      
      for (const p of possiblePaths) {
        if (fs.existsSync(p)) return p;
      }
    } else if (isLinux) {
      const possiblePaths = [
        '/usr/bin/ollama',
        '/usr/local/bin/ollama'
      ];
      
      for (const p of possiblePaths) {
        if (fs.existsSync(p)) return p;
      }
    }
    
    return null;
  }

  /**
   * Check if the specified model is available
   * 
   * @returns {Promise<boolean>} True if model is available
   */
  async checkModelAvailable() {
    try {
      const response = await axios.get(`${this.serverUrl}/api/tags`);
      
      if (response.status !== 200) {
        return false;
      }
      
      const models = response.data.models || [];
      return models.some(model => model.name === this.modelName);
    } catch (error) {
      console.error('Error checking model availability:', error.message);
      return false;
    }
  }

  /**
   * Download the specified model
   * 
   * @returns {Promise<boolean>} True if downloaded successfully
   */
  async downloadModel() {
    try {
      console.log(`Downloading model: ${this.modelName}`);
      
      // Start model pull
      const response = await axios.post(`${this.serverUrl}/api/pull`, {
        name: this.modelName
      });
      
      if (response.status !== 200) {
        console.error('Failed to start model download');
        return false;
      }
      
      // Wait for download to complete (check every 2 seconds)
      for (let i = 0; i < 150; i++) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const available = await this.checkModelAvailable();
        if (available) {
          console.log(`Model ${this.modelName} downloaded successfully`);
          return true;
        }
      }
      
      console.error('Timeout waiting for model download');
      return false;
    } catch (error) {
      console.error('Error downloading model:', error.message);
      return false;
    }
  }

  /**
   * Get the status of the Ollama service
   * 
   * @returns {Object} Status object
   */
  async getStatus() {
    const running = await this.checkServerRunning();
    const modelAvailable = running ? await this.checkModelAvailable() : false;
    
    return {
      running,
      modelAvailable,
      modelName: this.modelName,
      ready: this.isReady,
      error: this.lastError
    };
  }

  /**
   * Process a query to the AI model
   * 
   * @param {string} prompt User prompt
   * @param {string} context Code context
   * @returns {Promise<Object>} Response from AI
   */
  async processQuery(prompt, context) {
    if (!this.isReady) {
      return { error: 'AI service not ready' };
    }
    
    try {
      // Prepare full prompt with context
      const fullPrompt = this.preparePrompt(prompt, context);
      
      // Send to Ollama
      const response = await axios.post(`${this.serverUrl}/api/generate`, {
        model: this.modelName,
        prompt: fullPrompt,
        stream: false
      });
      
      if (response.status !== 200) {
        throw new Error(`Unexpected status: ${response.status}`);
      }
      
      return {
        success: true,
        response: response.data.response
      };
    } catch (error) {
      console.error('Error processing query:', error.message);
      return { error: `Failed to process query: ${error.message}` };
    }
  }

 /**
 * Prepare a full prompt including context
 * 
 * @param {string} prompt User prompt
 * @param {string} context Code context
 * @returns {string} Full prompt
 */
preparePrompt(prompt, context) {
  let fullPrompt = "You are CodeLve, an AI assistant that helps developers understand and modify code. ";
  fullPrompt += "You are an expert programmer with deep knowledge of software development, algorithms, and best practices. ";
  fullPrompt += "You excel at analyzing code, explaining concepts, fixing bugs, and generating new code.";
  
  fullPrompt += "\n\nWhen responding to code questions:";
  fullPrompt += "\n- Provide clear, concise explanations";
  fullPrompt += "\n- Highlight potential bugs or improvements";
  fullPrompt += "\n- Use code examples to illustrate concepts";
  
  fullPrompt += "\n\nWhen generating code:";
  fullPrompt += "\n- Create complete, well-structured solutions";
  fullPrompt += "\n- Follow language-specific best practices and style guides";
  fullPrompt += "\n- Include helpful comments";
  fullPrompt += "\n- Consider edge cases and error handling";
  
  if (context && context.trim()) {
    fullPrompt += "\n\nCODE CONTEXT:\n```\n" + context + "\n```\n\n";
    // Detect language based on context
    const fileExtension = context.includes("File:") ? 
      context.split("File:")[1].trim().split("\n")[0].split(".").pop() : "";
    
    if (fileExtension) {
      fullPrompt += `\nThe code appears to be in ${this.getLanguageName(fileExtension)}. `;
      fullPrompt += "Please consider language-specific features and best practices in your response.";
    }
  }
  
  fullPrompt += "\n\nUSER QUERY: " + prompt;
  return fullPrompt;
}

/**
 * Get a human-readable language name from file extension
 * 
 * @param {string} extension File extension
 * @returns {string} Language name
 */
getLanguageName(extension) {
  const languageMap = {
    "js": "JavaScript",
    "ts": "TypeScript",
    "py": "Python",
    "java": "Java",
    "c": "C",
    "cpp": "C++",
    "cs": "C#",
    "php": "PHP",
    "rb": "Ruby",
    "go": "Go",
    "rs": "Rust",
    "swift": "Swift",
    "kt": "Kotlin",
    "html": "HTML",
    "css": "CSS",
    "json": "JSON",
    "md": "Markdown",
    "sql": "SQL",
    "sh": "Shell/Bash",
    "jsx": "React JSX",
    "tsx": "React TSX"
  };
  
  return languageMap[extension.toLowerCase()] || extension;
}

  /**
   * Shutdown the Ollama service
   */
  async shutdown() {
    this.isReady = false;
    // For now, we don't actually stop the Ollama server
    // as it may be used by other applications
    console.log('Ollama service shut down');
  }
}

module.exports = OllamaService;