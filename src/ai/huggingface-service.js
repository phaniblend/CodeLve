/**
 * AI Service for CodeLve
 * 
 * Provides AI functionality for code assistance and generation
 */

const { HfInference } = require('@huggingface/inference');

class AIService {
  constructor() {
    this.isReady = false;
    this.lastError = null;
    // Internal model details not exposed to users
    this._modelId = 'mistralai/Mistral-7B-Instruct-v0.2';
    this._client = null;
this._apiKey = process.env.HF_API_KEY || "";  }

  /**
   * Initialize the AI service
   * 
   * @returns {Promise<boolean>} True if initialized successfully
   */
  async initialize() {
    try {
      console.log('Initializing CodeLve AI service...');
      
      // Initialize the backend client
      this._client = new HfInference(this._apiKey);
      
      // Verify connectivity with a small test
      try {
        await this._client.featureExtraction({
          model: 'sentence-transformers/paraphrase-albert-small-v2',
          inputs: 'Test connectivity'
        });
        this.isReady = true;
        console.log('CodeLve AI service initialized successfully');
      } catch (testError) {
        console.error('Failed to connect to AI backend:', testError);
        this.lastError = `Connection test failed: ${testError.message}`;
        return false;
      }
      
      return true;
    } catch (error) {
      this.lastError = `Error initializing AI service: ${error.message}`;
      console.error(this.lastError);
      return false;
    }
  }

  /**
   * Get the status of the AI service
   * 
   * @returns {Object} Status object
   */
  async getStatus() {
    return {
      running: this.isReady,
      modelAvailable: this.isReady,
      modelName: "CodeLve AI", // User-facing model name
      ready: this.isReady,
      error: this.lastError
    };
  }

  /**
   * Process a query to the AI
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
      const fullPrompt = this._preparePrompt(prompt, context);
      
      // Send to AI backend
      const response = await this._client.textGeneration({
        model: this._modelId,
        inputs: fullPrompt,
        parameters: {
          max_new_tokens: 512,
          temperature: 0.7,
          top_p: 0.95,
          do_sample: true
        }
      });
      
      if (!response || !response.generated_text) {
        throw new Error('Empty response from AI backend');
      }
      
      // Extract the relevant part of the response
      const processedResponse = this._processResponse(response.generated_text, fullPrompt);
      
      return {
        success: true,
        response: processedResponse
      };
    } catch (error) {
      console.error('Error processing query:', error.message);
      return { error: `Failed to process query: ${error.message}` };
    }
  }

  /**
   * Prepare a full prompt including context (internal method)
   * 
   * @param {string} prompt User prompt
   * @param {string} context Code context
   * @returns {string} Full prompt
   * @private
   */
  _preparePrompt(prompt, context) {
    let fullPrompt = "You are CodeLve, an AI assistant that helps developers understand and modify code. ";
    fullPrompt += "You analyze code and provide clear, concise explanations and suggestions. ";
    fullPrompt += "When asked to create new code files or components, provide complete, well-structured code that follows best practices.";
    
    if (context && context.trim()) {
      fullPrompt += "\n\nCODE CONTEXT:\n```\n" + context + "\n```\n\n";
    }
    
    fullPrompt += "USER QUERY: " + prompt;
    return fullPrompt;
  }

  /**
   * Process the raw response from the AI backend (internal method)
   * 
   * @param {string} rawResponse Raw response from AI
   * @param {string} originalPrompt Original prompt sent to AI
   * @returns {string} Processed response
   * @private
   */
  _processResponse(rawResponse, originalPrompt) {
    // Remove the original prompt if it's echoed back
    if (rawResponse.startsWith(originalPrompt)) {
      return rawResponse.substring(originalPrompt.length).trim();
    }
    
    return rawResponse.trim();
  }

  /**
   * Shutdown the AI service
   */
  async shutdown() {
    this.isReady = false;
    console.log('CodeLve AI service shut down');
  }
}

module.exports = AIService;