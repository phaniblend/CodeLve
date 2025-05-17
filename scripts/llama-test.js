/**
 * llama.cpp Integration Test for CodeLve
 * 
 * Tests the llama.cpp integration through llama-node package
 */

const path = require('path');
const os = require('os');
const fs = require('fs');
const { LLamaNode } = require('llama-node');
const { LLamaNodeOption } = require('llama-node/dist/llama-node-options');

// Config
const homeDir = os.homedir();
const modelsDir = path.join(homeDir, '.codelve', 'models');

/**
 * Test llama.cpp integration
 */
async function testLlamaIntegration() {
  console.log('\n=== Testing llama.cpp Integration ===\n');
  
  // Check for model files
  console.log('Checking for model files...');
  
  if (!fs.existsSync(modelsDir)) {
    console.error(`Models directory not found: ${modelsDir}`);
    console.error('Please run download-models.js first to download a model.');
    process.exit(1);
  }
  
  const modelFiles = fs.readdirSync(modelsDir);
  const ggufModels = modelFiles.filter(file => file.endsWith('.gguf'));
  
  if (ggufModels.length === 0) {
    console.error('No language models found.');
    console.error('Please run download-models.js first to download a model.');
    process.exit(1);
  }
  
  // Use the first model found
  const modelPath = path.join(modelsDir, ggufModels[0]);
  console.log(`Using model: ${ggufModels[0]}`);
  console.log(`Full path: ${modelPath}`);
  
  try {
    // Initialize llama.cpp
    console.log('\nInitializing llama.cpp...');
    
    const llama = new LLamaNode();
    
    // Set options
    const options = new LLamaNodeOption();
    options.modelPath = modelPath;
    options.enableLogging = true;
    options.nCtx = 2048;
    options.seed = -1; // Random seed
    
    // Load model
    console.log('Loading model...');
    await llama.load(options);
    console.log('Model loaded successfully!');
    
    // Prepare inference parameters
    const inferenceParams = {
      nThreads: Math.min(4, os.cpus().length), 
      nTokPredict: 512,
      topK: 40,
      topP: 0.95,
      temp: 0.8,
      repeatPenalty: 1.1
    };
    
    // Run inference
    console.log('\nRunning inference...');
    console.log('Prompt: "Explain what a language model is in one paragraph."');
    
    const prompt = "Explain what a language model is in one paragraph.";
    
    console.log('\nGenerating response...');
    console.time('Inference time');
    
    const result = await llama.generate(prompt, inferenceParams);
    
    console.timeEnd('Inference time');
    
    console.log('\nGenerated response:');
    console.log('==================');
    console.log(result);
    console.log('==================');
    
    // Free resources
    console.log('\nFreeing resources...');
    await llama.free();
    
    console.log('\nTest completed successfully!');
  } catch (error) {
    console.error('\nError testing llama.cpp integration:', error);
    process.exit(1);
  }
}

// Run the test
testLlamaIntegration().catch(error => {
  console.error('Unhandled error during test:', error);
  process.exit(1);
});