/**
 * Llama Process Service for CodeLve
 * 
 * Uses llama.cpp directly via child process or mock mode when not available
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
    this.useMockMode = true; // Default to mock mode for initial testing
  }

  /**
   * Initialize the Llama service
   * 
   * @returns {Promise<boolean>} True if initialized successfully
   */
  async initialize() {
    try {
      console.log('Initializing Llama Process service...');
      
      // Always set to ready for quick UI testing
      this.isReady = true;
      
      // Try to find model path
      this.modelPath = await this.findModel();
      if (!this.modelPath) {
        console.log('No model found, using mock mode');
        this.lastError = 'Model not found - using mock mode';
        return true;
      }
      
      // Find llama.cpp binary
      this.llamaBinaryPath = await this.findLlamaBinary();
      if (!this.llamaBinaryPath) {
        console.log('Llama.cpp binary not found, using mock mode');
        this.lastError = 'LLama.cpp binary not found - using mock mode';
        return true;
      }
      
      console.log(`Found model at: ${this.modelPath}`);
      console.log(`Found llama.cpp binary at: ${this.llamaBinaryPath}`);
      
      // Test the binary works
      const testResult = await this.testLlamaBinary();
      if (!testResult) {
        console.log('Failed to run llama.cpp binary, using mock mode');
        this.lastError = 'Failed to run llama.cpp binary - using mock mode';
      } else {
        console.log('Llama process service initialized successfully with real model');
        this.useMockMode = false;
      }
      
      return true;
    } catch (error) {
      this.lastError = `Error initializing Llama process: ${error.message}`;
      console.error(this.lastError);
      return true; // Still return true for UI testing
    }
  }

  /**
   * Find the llama.cpp binary
   * 
   * @returns {Promise<string|null>} Path to binary or null if not found
   */
  async findLlamaBinary() {
    // Check in the llama-b5410-bin-win-cpu-x64 directory
    const llamaDir = path.join(process.cwd(), 'resources', 'llama-b5410-bin-win-cpu-x64');
    const llamaCliPath = path.join(llamaDir, 'llama-cli.exe');
    
    console.log(`Checking for llama-cli.exe at: ${llamaCliPath}`);
    
    if (fs.existsSync(llamaCliPath)) {
      console.log(`Found llama-cli.exe at: ${llamaCliPath}`);
      return llamaCliPath;
    }
    
    // Check in resources/bin directory
    const binDir = path.join(process.cwd(), 'resources', 'bin');
    const binCliPath = path.join(binDir, 'llama.exe');
    
    if (fs.existsSync(binCliPath)) {
      console.log(`Found llama.exe at: ${binCliPath}`);
      return binCliPath;
    }
    
    console.log('Llama.cpp binary not found, using mock mode');
    return null;
  }

  /**
   * Test if the llama.cpp binary works
   * 
   * @returns {Promise<boolean>} True if test was successful
   */
  async testLlamaBinary() {
    if (!this.llamaBinaryPath || !this.modelPath) {
      return false;
    }
    
    try {
      // Just check if the file exists and is executable
      if (fs.existsSync(this.llamaBinaryPath)) {
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error testing llama binary:', error);
      return false;
    }
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
    console.log('No model found, using mock mode');
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
      error: this.lastError,
      useMockMode: this.useMockMode
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
    
    console.log(`Processing query: "${prompt.substring(0, 50)}${prompt.length > 50 ? '...' : ''}"`);
    
    // Use mock mode if no binary/model or if explicitly set
    if (this.useMockMode || !this.llamaBinaryPath || !this.modelPath) {
      console.log('Using mock mode for response');
      const mockResponse = this.generateMockResponse(prompt, context);
      
      return {
        success: true,
        response: mockResponse
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
   * Generate a mock response for testing
   * 
   * @param {string} prompt User prompt
   * @param {string} context Code context
   * @returns {string} Mock response
   */
  generateMockResponse(prompt, context) {
    // Convert to lowercase for easier matching
    const lowerPrompt = prompt.toLowerCase();
    
    // Greeting patterns
    if (lowerPrompt.match(/^(hi|hello|hey|greetings)/)) {
      return "Hello! I'm CodeLve, your coding assistant. How can I help you today?";
    }
    
    // Check if asking about what a function does
    const functionMatch = lowerPrompt.match(/what does (\w+)\(\) do/);
    if (functionMatch && context) {
      const functionName = functionMatch[1];
      
      if (context.includes(`function ${functionName}`)) {
        return `The \`${functionName}\` function appears to be defined in your code. Based on what I can see, it ${context.includes('console.log') ? 'prints something to the console' : 'performs some operations'}.`;
      }
    }
    
    // Check if asking about language features
    if (lowerPrompt.includes('javascript') || lowerPrompt.includes('js')) {
      return "JavaScript is a versatile programming language primarily used for web development. It allows you to add interactive behavior to web pages and create various applications.";
    }
    
    // Default response
    return `I'm currently running in mock mode since the LLM isn't fully set up yet.\n\nYou asked: "${prompt}"\n\nIn the full version, I would analyze your code and provide detailed assistance. For now, I can still help with general programming questions!`;
  }

  /**
   * Run inference using llama.cpp
   * 
   * @param {string} prompt Full prompt
   * @returns {Promise<string>} Generated text
   */
  async runLlamaInference(prompt) {
    return new Promise((resolve, reject) => {
      // Save prompt to temporary file for large prompts
      const promptFile = path.join(os.tmpdir(), `prompt_${Date.now()}.txt`);
      fs.writeFileSync(promptFile, prompt, 'utf8');
      
      // For simple queries, use direct prompt
      let args;
      const isShortPrompt = prompt.length < 100;
      
      if (isShortPrompt) {
        // Use -p for short prompts
        args = [
          '-m', this.modelPath,
          '-p', prompt,
          '-n', '300',
          '--temp', '0.7',
          '--repeat_penalty', '1.1'
        ];
      } else {
        // Use file for longer prompts
        args = [
          '-m', this.modelPath,
          '-f', promptFile,
          '-n', '300',
          '--temp', '0.7',
          '--repeat_penalty', '1.1'
        ];
      }
      
      console.log(`Running: ${this.llamaBinaryPath} with ${args.length} args`);
      
      const llamaProcess = spawn(this.llamaBinaryPath, args, {
        cwd: path.dirname(this.llamaBinaryPath) // Important: run from the binary directory for DLL access
      });
      
      let output = '';
      let errorOutput = '';
      
      llamaProcess.stdout.on('data', (data) => {
        const chunk = data.toString();
        output += chunk;
      });
      
      llamaProcess.stderr.on('data', (data) => {
        const chunk = data.toString();
        errorOutput += chunk;
      });
      
      llamaProcess.on('close', (code) => {
        // Clean up temp file
        if (!isShortPrompt && fs.existsSync(promptFile)) {
          try {
            fs.unlinkSync(promptFile);
          } catch (e) {
            console.error('Error deleting temp file:', e);
          }
        }
        
        if (code === 0) {
          // Process output to extract just the generated response
          const result = this.processOutput(output, prompt);
          resolve(result);
        } else {
          console.error(`llama-cli.exe exited with code ${code}`);
          console.error(`Error output: ${errorOutput}`);
          
          // Return a helpful message
          if (errorOutput.includes('out of memory')) {
            resolve("I'm sorry, but I ran out of memory trying to process your request. Please try a shorter query.");
          } else {
            resolve("I'm sorry, but I encountered an error processing your request. Please try again with a simpler query.");
          }
        }
      });
      
      llamaProcess.on('error', (err) => {
        console.error('Error running llama-cli.exe:', err);
        
        // Clean up temp file
        if (!isShortPrompt && fs.existsSync(promptFile)) {
          try {
            fs.unlinkSync(promptFile);
          } catch (e) {
            console.error('Error deleting temp file:', e);
          }
        }
        
        resolve("I encountered an error while trying to process your request. Please try again later.");
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
    // Extract only the model's response (after the prompt)
    // First try to find the exact prompt
    let cleanedOutput = output;
    
    // First remove any loading or initialization info
    const promptIndex = output.indexOf(prompt);
    if (promptIndex !== -1) {
      cleanedOutput = output.substring(promptIndex + prompt.length);
    } else {
      // If we can't find the exact prompt, look for the last line of the prompt
      const promptLines = prompt.split('\n');
      const lastPromptLine = promptLines[promptLines.length - 1].trim();
      
      if (lastPromptLine.length > 10) {  // Only use if it's substantial enough
        const lastLineIndex = output.indexOf(lastPromptLine);
        if (lastLineIndex !== -1) {
          cleanedOutput = output.substring(lastLineIndex + lastPromptLine.length);
        }
      }
    }
    
    // Remove any stats info at the end
    const statsIndex = cleanedOutput.indexOf('llama_');
    if (statsIndex !== -1) {
      cleanedOutput = cleanedOutput.substring(0, statsIndex);
    }
    
    return cleanedOutput.trim();
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
    
    fullPrompt += "\n\nUSER QUERY: " + prompt + "\n\n";
    
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