/**
 * LLama Service for CodeLve
 * 
 * Manages direct integration with llama.cpp via Node.js bindings
 */

const path = require('path');
const os = require('os');
const fs = require('fs');
const { spawn } = require('child_process');

// Import llama-node in a different way
let LlamaNode;
try {
  const llamaNode = require('llama-node');
  LlamaNode = llamaNode.LLamaNode || llamaNode.default;
} catch (error) {
  console.error('Failed to import llama-node:', error);
}

class LlamaService {
  constructor() {
    this.modelName = 'mistral';
    this.isReady = false;
    this.lastError = null;
    this.maxRetries = 3;
    this.llamaModel = null;
    this.modelPath = null;
    this.inferenceParams = {
      nThreads: Math.min(4, os.cpus().length), // Use up to 4 threads
      nTokPredict: 2048,                       // Generate up to 2048 tokens
      topK: 40,
      topP: 0.95,
      temp: 0.8,
      repeatPenalty: 1.1
    };
  }

  /**
   * Initialize the Llama service
   * 
   * @returns {Promise<boolean>} True if initialized successfully
   */
  async initialize() {
    try {
      console.log('Initializing Llama service...');
      
      // Find model path
      this.modelPath = await this.findOrDownloadModel();
      if (!this.modelPath) {
        this.lastError = 'Failed to find or download model';
        return false;
      }
      
      console.log(`Found model at: ${this.modelPath}`);
      
      // Check if we have llama-node loaded
      if (!LlamaNode) {
        this.lastError = 'llama-node package not available';
        console.error(this.lastError);
        
        // Still set to ready for UI testing
        this.isReady = true;
        console.log('Llama service initialized in mock mode');
        return true;
      }
      
      // Initialize llama.cpp
      try {
        await this.initializeLlama();
      } catch (error) {
        this.lastError = `Failed to initialize llama.cpp: ${error.message}`;
        console.error(this.lastError);
        
        // Still set to ready for UI testing
        this.isReady = true;
        console.log('Llama service initialized in mock mode after initialization error');
        return true;
      }
      
      this.isReady = true;
      console.log('Llama service initialized successfully');
      return true;
    } catch (error) {
      this.lastError = `Error initializing Llama: ${error.message}`;
      console.error(this.lastError);
      
      // Still set to ready for UI testing
      this.isReady = true;
      console.log('Llama service initialized in mock mode after error');
      return true;
    }
  }

  /**
   * Initialize llama.cpp with the model
   * 
   * @returns {Promise<void>}
   */
  async initializeLlama() {
    try {
      // Create a new instance
      this.llamaModel = new LlamaNode();
      
      // Set up options directly
      const options = {
        modelPath: this.modelPath,
        enableLogging: false,
        nCtx: 4096,
        seed: -1 // Random seed
      };
      
      // Load the model
      await this.llamaModel.load(options);
      
      console.log('Llama model loaded successfully');
    } catch (error) {
      console.error('Error initializing llama.cpp:', error);
      throw error;
    }
  }

  /**
   * Find existing model or download if not available
   * 
   * @returns {Promise<string|null>} Path to model or null if not found
   */
  async findOrDownloadModel() {
    // Check local project models directory first
    const projectModelsDir = path.join(process.cwd(), 'models');
    const projectModelPath = path.join(projectModelsDir, `${this.modelName}.gguf`);
    const alternateProjectModelPath = path.join(projectModelsDir, `mistral-7b-v0.1.Q4_0.gguf`);
    
    // Define user home models directory
    const homeModelsDir = path.join(os.homedir(), '.codelve', 'models');
    const homeModelPath = path.join(homeModelsDir, `${this.modelName}.gguf`);
    const alternateHomeModelPath = path.join(homeModelsDir, `mistral-7b-v0.1.Q4_0.gguf`);
    
    // Ensure home directory exists
    if (!fs.existsSync(homeModelsDir)) {
      fs.mkdirSync(homeModelsDir, { recursive: true });
    }
    
    // Check in project directory first
    if (fs.existsSync(projectModelPath)) {
      console.log(`Model found at: ${projectModelPath}`);
      return projectModelPath;
    }
    
    if (fs.existsSync(alternateProjectModelPath)) {
      console.log(`Model found at: ${alternateProjectModelPath}`);
      return alternateProjectModelPath;
    }
    
    // Check in home directory next
    if (fs.existsSync(homeModelPath)) {
      console.log(`Model found at: ${homeModelPath}`);
      return homeModelPath;
    }
    
    if (fs.existsSync(alternateHomeModelPath)) {
      console.log(`Model found at: ${alternateHomeModelPath}`);
      return alternateHomeModelPath;
    }
    
    // Model not found, need to download
    console.log(`Model not found, downloading ${this.modelName}...`);
    
    // Define download URL
    const downloadUrl = this.getModelDownloadUrl(this.modelName);
    if (!downloadUrl) {
      console.error(`No download URL available for model: ${this.modelName}`);
      return null;
    }
    
    try {
      // Download the model
      await this.downloadModel(downloadUrl, homeModelPath);
      
      // Verify file exists after download
      if (fs.existsSync(homeModelPath)) {
        console.log(`Model downloaded successfully to: ${homeModelPath}`);
        return homeModelPath;
      } else {
        console.error('Model file not found after download');
        return null;
      }
    } catch (error) {
      console.error('Error downloading model:', error);
      return null;
    }
  }

  /**
   * Get download URL for the specified model
   * 
   * @param {string} modelName Name of the model
   * @returns {string|null} Download URL or null if not supported
   */
  getModelDownloadUrl(modelName) {
    // Map of supported models to their download URLs
    const modelUrls = {
      'mistral': 'https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q4_K_M.gguf',
      'llama2': 'https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf'
    };
    
    return modelUrls[modelName] || null;
  }

  /**
   * Download a model file
   * 
   * @param {string} url Download URL
   * @param {string} outputPath Output file path
   * @returns {Promise<boolean>} True if successful
   */
  async downloadModel(url, outputPath) {
    return new Promise((resolve, reject) => {
      // We'll use fetch or a similar HTTP library for production
      // For now, we can use a utility like wget or curl via child process
      const platform = os.platform();
      let downloadProcess;
      
      if (platform === 'win32') {
        // Use PowerShell on Windows
        downloadProcess = spawn('powershell', [
          '-Command',
          `Invoke-WebRequest -Uri "${url}" -OutFile "${outputPath}"`
        ]);
      } else {
        // Use curl on macOS/Linux
        downloadProcess = spawn('curl', ['-L', url, '-o', outputPath]);
      }
      
      let stderr = '';
      
      downloadProcess.stderr.on('data', (data) => {
        stderr += data.toString();
        console.log(`Download progress: ${data.toString()}`);
      });
      
      downloadProcess.on('close', (code) => {
        if (code === 0) {
          resolve(true);
        } else {
          reject(new Error(`Download failed with code ${code}: ${stderr}`));
        }
      });
      
      downloadProcess.on('error', (err) => {
        reject(err);
      });
    });
  }

  /**
   * Get the status of the Llama service
   * 
   * @returns {Object} Status object
   */
  async getStatus() {
    return {
      running: this.llamaModel !== null || this.isReady, // Consider ready even in mock mode
      modelAvailable: this.modelPath !== null,
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
      // Create the prompt safely
      let fullPrompt;
      try {
        fullPrompt = this.preparePrompt(prompt, context);
      } catch (promptError) {
        console.error('Error creating prompt:', promptError);
        // Fallback to a simpler prompt
        fullPrompt = `You are a coding assistant. Please help with this query: ${prompt}`;
        if (context) {
          fullPrompt += `\n\nContext:\n${context}`;
        }
      }
      
      // Use llama model if available, otherwise return mock response
      if (this.llamaModel) {
        try {
          const result = await this.llamaModel.generate(
            fullPrompt,
            this.inferenceParams
          );
          
          return {
            success: true,
            response: result
          };
        } catch (error) {
          console.error('Error during inference:', error);
          return {
            success: true,
            response: `[Mock response] I've analyzed your query: "${prompt}"\n\nThis is a temporary response until the AI model is properly integrated. The real model would analyze the code context and provide a helpful answer.`
          };
        }
      } else {
        // Return mock response for UI testing
        return {
          success: true,
          response: `[Mock response] I've analyzed your query: "${prompt}"\n\nThis is a temporary response until llama.cpp integration is complete. The real model would analyze the code context and provide a helpful answer.`
        };
      }
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
   * Shutdown the Llama service
   */
  async shutdown() {
    this.isReady = false;
    
    if (this.llamaModel) {
      try {
        // Clean up llama.cpp resources
        await this.llamaModel.free();
        this.llamaModel = null;
        console.log('Llama model resources freed');
      } catch (error) {
        console.error('Error shutting down Llama model:', error);
      }
    }
    
    console.log('Llama service shut down');
  }
}

module.exports = LlamaService;