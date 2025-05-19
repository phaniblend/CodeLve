/**
 * Llama Process Service for CodeLve
 *
 * Uses llama.cpp directly via child process or mock mode when not available
 */

const { spawn } = require("child_process");
const path = require("path");
const os = require("os");
const fs = require("fs");

class LlamaProcessService {
  constructor() {
    this.modelName = "mistral";
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
    console.log("Initializing Llama Process service...");

    // Find model path
    this.modelPath = await this.findModel();
    if (!this.modelPath) {
      this.lastError =
        "Model not found. Please make sure Mistral model is in the models directory.";
      console.error(this.lastError);
      return false;
    }

    console.log(`Found model at: ${this.modelPath}`);

    // Find llama.cpp binary
    this.llamaBinaryPath = await this.findLlamaBinary();
    if (!this.llamaBinaryPath) {
      this.lastError =
        "Failed to find llama.cpp binary. Please ensure it is installed correctly.";
      console.error(this.lastError);
      return false;
    }

    console.log(`Found llama.cpp binary at: ${this.llamaBinaryPath}`);

    // Test the binary works
    const testResult = await this.testLlamaBinary();
    if (!testResult) {
      this.lastError =
        "Failed to run llama.cpp binary. Please check file permissions and dependencies.";
      console.error(this.lastError);
      return false;
    }

    // Everything is good for basic initialization
    this.isReady = true;
    this.useMockMode = false;
    console.log("Llama process service initialized successfully");
    
    // Optionally test the model with a sample prompt
    // Only do this if we're in a development environment or if explicitly requested
    if (process.env.NODE_ENV === 'development' || process.env.TEST_MODEL === 'true') {
      console.log("Running model test...");
      const modelTestResult = await this.testModel();
      if (!modelTestResult) {
        console.warn("Model test was not successful, but continuing anyway");
        // Don't fail initialization, just warn
      } else {
        console.log("Model test successful!");
      }
    }
    
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
    // Check in the llama-b5410-bin-win-cpu-x64 directory
    const llamaDir = path.join(
      process.cwd(),
      "resources",
      "llama-b5410-bin-win-cpu-x64"
    );
    const llamaCliPath = path.join(llamaDir, "llama-cli.exe");

    console.log(`Checking for llama-cli.exe at: ${llamaCliPath}`);

    if (fs.existsSync(llamaCliPath)) {
      console.log(`Found llama-cli.exe at: ${llamaCliPath}`);
      return llamaCliPath;
    }

    // Check in resources/bin directory
    const binDir = path.join(process.cwd(), "resources", "bin");
    const binCliPath = path.join(binDir, "llama.exe");

    if (fs.existsSync(binCliPath)) {
      console.log(`Found llama.exe at: ${binCliPath}`);
      return binCliPath;
    }

    console.log("Llama.cpp binary not found, using mock mode");
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
      console.error("Error testing llama binary:", error);
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
    const projectModelsDir = path.join(process.cwd(), "models");
    const projectModelPath = path.join(
      projectModelsDir,
      `${this.modelName}.gguf`
    );
    const alternateProjectModelPath = path.join(
      projectModelsDir,
      `mistral-7b-v0.1.Q4_0.gguf`
    );

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
    console.log("No model found, using mock mode");
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
      useMockMode: this.useMockMode,
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
    return { error: 'AI service not ready. ' + (this.lastError || 'Unknown error.') };
  }
  
  console.log(`Processing query: "${prompt.substring(0, 50)}${prompt.length > 50 ? '...' : ''}"`);
  
  try {
    // Check if the binary and model exist
    if (!this.llamaBinaryPath || !this.modelPath) {
      console.log('Model or binary not available, using mock mode');
      const mockResponse = this.generateMockResponse(prompt, context);
      return {
        success: true,
        response: mockResponse,
        mock: true
      };
    }
    
    // Prepare full prompt with context
    const fullPrompt = this.preparePrompt(prompt, context);
    console.log('Prepared full prompt, running inference...');
    
    // Run llama.cpp with the prompt
    const result = await this.runLlamaInference(fullPrompt);
    
    // Extract just the model response part, filtering out the prompt
    const cleanResponse = this.extractResponseFromOutput(result, prompt);
    
    // Validate the response
    if (!cleanResponse || cleanResponse.length < 10) {
      console.warn('Got empty or too short response from model, using fallback');
      return {
        success: true,
        response: this.generateMockResponse(prompt, context),
        mock: true
      };
    }
    
    return {
      success: true,
      response: cleanResponse
    };
  } catch (error) {
    console.error('Error processing query:', error);
    
    // Fall back to mock response on error
    console.log('Falling back to mock mode due to error');
    const mockResponse = this.generateMockResponse(prompt, context);
    
    return { 
      success: true,
      response: mockResponse,
      mock: true
    };
  }
}

  /**
 * Extract just the AI response from the full output
 * 
 * @param {string} output Full output including prompt and response
 * @param {string} prompt Original user prompt
 * @returns {string} Clean response
 */

extractResponseFromOutput(output, prompt) {
  // Find the assistant's response after the instruction format
  const marker = "[/INST]";
  let response = output;
  
  const markerIndex = output.indexOf(marker);
  if (markerIndex !== -1) {
    // Extract everything after the marker
    response = output.substring(markerIndex + marker.length).trim();
  }
  
  // Remove any "Assistant:" prefix if present
  response = response.replace(/^Assistant:\s*/i, "");
  
  // Clean up any trailing user messages or prompts
  const userPatterns = [
    "User:", 
    "<User>",
    "Human:",
    "<s>[INST]",
    "USER QUERY:"
  ];
  
  for (const pattern of userPatterns) {
    const nextUserIndex = response.indexOf(pattern);
    if (nextUserIndex !== -1) {
      response = response.substring(0, nextUserIndex).trim();
    }
  }
  
  // Remove any strange markdown artifacts or model-specific tokens
  response = response
    .replace(/<\/?s>/g, "") // Remove <s> and </s> tags
    .replace(/\[end of text\]/gi, "") // Remove [end of text] markers
    .trim();
  
  return response;
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
        return `The \`${functionName}\` function appears to be defined in your code. Based on what I can see, it ${
          context.includes("console.log")
            ? "prints something to the console"
            : "performs some operations"
        }.`;
      }
    }

    // Check if asking about language features
    if (lowerPrompt.includes("javascript") || lowerPrompt.includes("js")) {
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
    // Create temporary file for the prompt
    const tempDir = os.tmpdir();
    const promptFile = path.join(tempDir, `llama_prompt_${Date.now()}.txt`);
    
    try {
      // Write prompt to file
      fs.writeFileSync(promptFile, prompt, "utf8");
      
      console.log(`Saved prompt to ${promptFile}`);
      console.log(`Running inference with model: ${this.modelPath}`);
      
      // Build command arguments - optimized for Mistral instruct
      const args = [
        "-m", this.modelPath,        // Model path
        "-f", promptFile,            // Use prompt file
        "-n", "1024",                // Increase max tokens to generate
        "--temp", "0.1",             // Very low temperature for deterministic responses
        "--top_k", "40",             // Use top-k sampling
        "--top_p", "0.95",           // Slightly higher top-p value
        "--repeat_penalty", "1.3",   // Increased repeat penalty
        "--ctx-size", "4096",        // Increased context size
        "--grammar-file", "",        // No grammar file
        "--reverse-prompt", "User:", // Stop generation when encountering a new user message
        "--seed", "42",              // Fixed seed for reproducibility
        "--mirostat", "1",           // Enable Mirostat sampling
        "--mirostat-lr", "0.1",      // Mirostat learning rate
        "--mirostat-ent", "5.0",     // Mirostat target entropy
        "-c", "4096"                 // Context window size (alternative format)
      ];
      
      console.log(`Launching ${this.llamaBinaryPath} with arguments:`, args);
      
      // Run llama.cpp
      const llamaProcess = spawn(this.llamaBinaryPath, args, {
        cwd: path.dirname(this.llamaBinaryPath) // Run from binary directory for DLL access
      });
      
      let output = "";
      let errorOutput = "";
      
      // Collect stdout
      llamaProcess.stdout.on("data", (data) => {
        const chunk = data.toString();
        output += chunk;
        // Log progress (optional)
        if (output.length % 500 === 0) {
          console.log(`Generated ${output.length} characters so far...`);
        }
      });
      
      // Collect stderr
      llamaProcess.stderr.on("data", (data) => {
        const chunk = data.toString();
        console.error("Llama error output:", chunk);
        errorOutput += chunk;
      });
      
      // Add timeout for long-running processes
      const timeout = setTimeout(() => {
        console.warn("Inference is taking too long, terminating process");
        llamaProcess.kill();
        reject(new Error("Inference timed out after 60 seconds"));
      }, 60000); // 60 second timeout
      
      // Handle process completion
      llamaProcess.on("close", (code) => {
        clearTimeout(timeout); // Clear the timeout
        
        // Clean up temp file
        try {
          fs.unlinkSync(promptFile);
        } catch (e) {
          console.warn("Error removing temp file:", e);
        }
        
        if (code === 0) {
          console.log("Llama inference completed successfully");
          // Check if we got a meaningful response
          if (output && output.length > prompt.length) {
            resolve(output);
          } else {
            console.error("Empty or too short response from model");
            reject(new Error("Model returned empty or too short response"));
          }
        } else {
          console.error(`Llama process exited with code ${code}`);
          console.error("Error output:", errorOutput);
          reject(new Error(`Llama process failed with code ${code}: ${errorOutput}`));
        }
      });
      
      // Handle spawn error
      llamaProcess.on("error", (err) => {
        clearTimeout(timeout); // Clear the timeout
        console.error("Error running llama process:", err);
        // Clean up temp file
        try {
          fs.unlinkSync(promptFile);
        } catch (e) {
          console.warn("Error removing temp file:", e);
        }
        reject(err);
      });
      
    } catch (err) {
      console.error("Error in runLlamaInference:", err);
      // Clean up temp file if it was created
      try {
        if (fs.existsSync(promptFile)) {
          fs.unlinkSync(promptFile);
        }
      } catch (e) {
        console.warn("Error removing temp file:", e);
      }
      reject(err);
    }
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
      const promptLines = prompt.split("\n");
      const lastPromptLine = promptLines[promptLines.length - 1].trim();

      if (lastPromptLine.length > 10) {
        // Only use if it's substantial enough
        const lastLineIndex = output.indexOf(lastPromptLine);
        if (lastLineIndex !== -1) {
          cleanedOutput = output.substring(
            lastLineIndex + lastPromptLine.length
          );
        }
      }
    }

    // Remove any stats info at the end
    const statsIndex = cleanedOutput.indexOf("llama_");
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
  // Clear, structured prompt for Mistral with proper delimiters
  let fullPrompt = "<s>[INST]\n";
  
  // System instruction
  fullPrompt += "You are CodeLve, an AI coding assistant that helps developers understand and improve their code. ";
  fullPrompt += "You provide clear explanations, identify issues, and suggest improvements. ";
  fullPrompt += "You are knowledgeable about programming languages, algorithms, and best practices.\n\n";
  
  // Add code context if available
  if (context && context.trim()) {
    fullPrompt += "Below is the code I'm working with:\n\n" + context + "\n\n";
  }
  
  // Add the user query
  fullPrompt += "User: " + prompt + "\n\n";
  
  // Close instruction tag
  fullPrompt += "Assistant: [/INST]\n\n";
  
  return fullPrompt;
}
async testModel() {
  if (!this.isReady || !this.llamaBinaryPath || !this.modelPath) {
    console.error('Model not ready for testing');
    return false;
  }
  
  try {
    console.log('Running test prompt through model...');
    
    const testPrompt = this.preparePrompt(
      "Write a simple JavaScript function that adds two numbers", 
      ""
    );
    
    const result = await this.runLlamaInference(testPrompt);
    const cleanResponse = this.extractResponseFromOutput(result);
    
    console.log('Test response:', cleanResponse.substring(0, 100) + '...');
    
    // Check if response contains code
    const codeBlockCount = (cleanResponse.match(/```/g) || []).length;
    const hasCode = cleanResponse.includes('function') && 
                   (cleanResponse.includes('return') || 
                    cleanResponse.includes('console.log')) && 
                   codeBlockCount >= 2;
    
    if (hasCode) {
      console.log('Model test successful - response contains code');
      return true;
    } else {
      console.warn('Model test completed but response may not be optimal');
      console.warn('Response did not contain expected code elements');
      return false;
    }
  } catch (error) {
    console.error('Error testing model:', error);
    return false;
  }
}
  /**
   * Get a human-readable language name from file extension
   *
   * @param {string} extension File extension
   * @returns {string} Language name
   */
  getLanguageName(extension) {
    const languageMap = {
      js: "JavaScript",
      ts: "TypeScript",
      py: "Python",
      java: "Java",
      c: "C",
      cpp: "C++",
      cs: "C#",
      php: "PHP",
      rb: "Ruby",
      go: "Go",
      rs: "Rust",
      swift: "Swift",
      kt: "Kotlin",
      html: "HTML",
      css: "CSS",
      json: "JSON",
      md: "Markdown",
      sql: "SQL",
      sh: "Shell/Bash",
      jsx: "React JSX",
      tsx: "React TSX",
    };

    return languageMap[extension.toLowerCase()] || extension;
  }

  /**
   * Shutdown the Llama service
   */
  async shutdown() {
    this.isReady = false;
    console.log("Llama process service shut down");
  }
}

module.exports = LlamaProcessService;
