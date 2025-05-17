/**
 * Llama Process Service for CodeLve
 * 
 * Uses llama.cpp directly via child process
 */

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

class LlamaProcessService {
  constructor() {
    this.modelName = 'mistral';
    this.isReady = false;
    this.lastError = null;
    this.modelPath = null;
    this.llamaProcess = null;
    this.llamaBinaryPath = null;
  }

  /**
   * Initialize the Llama service
   * 
   * @returns {Promise<boolean>} True if initialized successfully
   */
  async initialize() {
    try {
      console.log('Initializing Llama Process service...');
      
      // Find model path
      this.modelPath = await this.findModel();
      if (!this.modelPath) {
        this.lastError = 'Failed to find model';
        return false;
      }
      
      // Find llama.cpp binary
      this.llamaBinaryPath = await this.findLlamaBinary();
      if (!this.llamaBinaryPath) {
        this.lastError = 'Failed to find llama.cpp binary';
        // Continue anyway for testing UI
        this.isReady = true;
        return true;
      }
      
      console.log(`Found model at: ${this.modelPath}`);
      console.log(`Found llama.cpp binary at: ${this.llamaBinaryPath}`);
      
      // Test the binary works
      const testResult = await this.testLlamaBinary();
      if (!testResult) {
        this.lastError = 'Failed to run llama.cpp binary';
        // Continue anyway for testing UI
        this.isReady = true;
        return true;
      }
      
      this.isReady = true;
      console.log('Llama process service initialized successfully');
      return true;
    } catch (error) {
      this.lastError = `Error initializing Llama process: ${error.message}`;
      console.error(this.lastError);
      return false;
    }
  }

 /**
 * Find the llama.cpp binary
 * 
 * @returns {Promise<string|null>} Path to binary or null if not found
 */
async findLlamaBinary() {
  // Check common locations for llama.cpp binary
  const platform = os.platform();
  const isWindows = platform === 'win32';
  
  // Check in bundled location first
  const resourcesPath = process.resourcesPath || path.join(process.cwd(), 'resources');
  console.log(`Looking for llama binary in: ${resourcesPath}`);
  
  const bundledPath = path.join(resourcesPath, 'bin', 
    isWindows ? 'llama.exe' : 'llama');
  
  console.log(`Checking for llama binary at: ${bundledPath}`);
  console.log(`File exists: ${fs.existsSync(bundledPath)}`);
  
  if (fs.existsSync(bundledPath)) {
    return bundledPath;
  }
  
  // Check the current directory structure
  console.log('Binary not found, listing bin directory contents:');
  try {
    const binPath = path.join(resourcesPath, 'bin');
    if (fs.existsSync(binPath)) {
      const files = fs.readdirSync(binPath);
      console.log(`Files in bin directory: ${files.join(', ')}`);
    } else {
      console.log('bin directory does not exist');
    }
  } catch (err) {
    console.error('Error listing bin directory:', err);
  }
  
  // Try an alternative path
  const altPath = path.join(process.cwd(), 'resources', 'bin', 
    isWindows ? 'llama.exe' : 'llama');
  
  console.log(`Checking alternative path: ${altPath}`);
  console.log(`File exists: ${fs.existsSync(altPath)}`);
  
  if (fs.existsSync(altPath)) {
    return altPath;
  }
  
  console.log('Llama.cpp binary not found in any location, using mock mode');
  return null;
}

/**
 * Test if the llama.cpp binary works
 * 
 * @returns {Promise<boolean>} True if test was successful
 */
async testLlamaBinary() {
  if (!this.llamaBinaryPath || !this.modelPath) {
    console.log('Cannot test binary: either binary path or model path is missing');
    return false;
  }
  
  console.log(`Testing binary at: ${this.llamaBinaryPath}`);
  
  return new Promise((resolve) => {
    // Run with --help to check it works
    console.log('Executing test command');
    const process = spawn(this.llamaBinaryPath, ['--help']);
    
    let stdout = '';
    let stderr = '';
    
    process.stdout.on('data', (data) => {
      stdout += data.toString();
      console.log(`Binary test stdout: ${data.toString()}`);
    });
    
    process.stderr.on('data', (data) => {
      stderr += data.toString();
      console.error(`Binary test stderr: ${data.toString()}`);
    });
    
    process.on('close', (code) => {
      console.log(`Binary test finished with code: ${code}`);
      if (code === 0 && (stdout.includes('llama') || stdout.includes('usage'))) {
        console.log('Llama.cpp binary test successful');
        resolve(true);
      } else {
        console.error(`Llama.cpp binary test failed with code ${code}`);
        console.error(`Stdout: ${stdout}`);
        console.error(`Stderr: ${stderr}`);
        resolve(false);
      }
    });
    
    process.on('error', (err) => {
      console.error('Error running llama.cpp binary:', err);
      resolve(false);
    });
  });
}
  /**
   * Find the model file
   * 
   * @returns {Promise<string|null>} Path to model or null if not found
   */
  async findModel() {
    // Check local project models directory first
    const projectModelsDir = path.join(process.cwd(), 'models');
    const projectModelPath = path.join(projectModelsDir, `${this.modelName}.gguf`);
    const alternateProjectModelPath = path.join(projectModelsDir, `mistral-7b-v0.1.Q4_0.gguf`);
    
    // Check in project directory first
    if (fs.existsSync(projectModelPath)) {
      console.log(`Model found at: ${projectModelPath}`);
      return projectModelPath;
    }
    
    if (fs.existsSync(alternateProjectModelPath)) {
      console.log(`Model found at: ${alternateProjectModelPath}`);
      return alternateProjectModelPath;
    }
    
    // Model not found
    console.error('No model found');
    return null;
  }

  /**
   * Get the status of the Llama service
   * 
   * @returns {Object} Status object
   */
  async getStatus() {
    return {
      running: this.isReady,
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
    
    // If we don't have the binary, use mock mode
    if (!this.llamaBinaryPath) {
      return {
        success: true,
        response: `[Mock response] I've analyzed your query: "${prompt}"\n\nThis is a temporary response until llama.cpp integration is complete. The real model would analyze the code context and provide a helpful answer.`
      };
    }
    
    try {
      // Prepare full prompt with context
      const fullPrompt = this.preparePrompt(prompt, context);
      
      // Run llama.cpp with the prompt
      const result = await this.runLlamaInference(fullPrompt);
      
      return {
        success: true,
        response: result
      };
    } catch (error) {
      console.error('Error processing query:', error.message);
      return { error: `Failed to process query: ${error.message}` };
    }
  }

  /**
   * Run inference using llama.cpp
   * 
   * @param {string} prompt Full prompt
   * @returns {Promise<string>} Generated text
   */
  async runLlamaInference(prompt) {
    return new Promise((resolve, reject) => {
      // Save prompt to temporary file
      const promptFile = path.join(os.tmpdir(), `prompt_${Date.now()}.txt`);
      fs.writeFileSync(promptFile, prompt, 'utf8');
      
      // Run llama.cpp with the prompt
      const args = [
        '--model', this.modelPath,
        '--file', promptFile,
        '--temp', '0.7',
        '--top-k', '40',
        '--top-p', '0.95',
        '--repeat-penalty', '1.1',
        '--ctx-size', '4096',
        '--n-predict', '2048'
      ];
      
      console.log(`Running llama.cpp: ${this.llamaBinaryPath} ${args.join(' ')}`);
      
      const llamaProcess = spawn(this.llamaBinaryPath, args);
      
      let output = '';
      let errorOutput = '';
      
      llamaProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      llamaProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
        console.error(`llama.cpp stderr: ${data.toString()}`);
      });
      
      llamaProcess.on('close', (code) => {
        // Remove prompt file
        try {
          fs.unlinkSync(promptFile);
        } catch (e) {
          console.error('Failed to delete prompt file:', e);
        }
        
        if (code === 0) {
          // Process output to remove the prompt
          const result = this.processOutput(output, prompt);
          resolve(result);
        } else {
          console.error(`llama.cpp exited with code ${code}`);
          resolve(`[Error response] There was an issue processing your query. The llama.cpp binary exited with code ${code}. Error output: ${errorOutput}`);
        }
      });
      
      llamaProcess.on('error', (err) => {
        // Remove prompt file
        try {
          if (fs.existsSync(promptFile)) {
            fs.unlinkSync(promptFile);
          }
        } catch (e) {
          console.error('Failed to delete prompt file after error:', e);
        }
        
        console.error('Error running llama.cpp:', err);
        resolve(`[Error response] There was an issue running the llama.cpp binary: ${err.message}`);
      });
    });
  }

  /**
   * Process the output from llama.cpp
   * 
   * @param {string} output Raw output
   * @param {string} prompt Original prompt
   * @returns {string} Processed output
   */
  processOutput(output, prompt) {
    // Remove the prompt from the beginning
    if (output.startsWith(prompt)) {
      output = output.substring(prompt.length);
    }
    
    // Clean up any artifacts
    output = output.trim();
    
    return output;
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
    console.log('Llama process service shut down');
  }
}

module.exports = LlamaProcessService;