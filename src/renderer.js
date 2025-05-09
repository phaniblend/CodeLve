/**
 * Renderer process entry point for CodeLve
 * 
 * Initializes the user interface and connects it to the backend services
 */

// Import UI components
const MainLayout = require('./ui/main-layout');
const ChatPanel = require('./chat/chat-panel');
const CodeContextProvider = require('./context/code-context-provider');

// Reference to the API exposed by the preload script
const { api, appInfo } = window;

// UI component instances
let mainLayout;
let chatPanel;
let codeContextProvider;

/**
 * Initialize the application UI
 */
async function initializeApp() {
  try {
    console.log(`Initializing CodeLve v${appInfo.version}`);
    
    // Create code context provider
    codeContextProvider = new CodeContextProvider();
    
    // Create main layout
    mainLayout = new MainLayout();
    const { editorContainer, chatContainer } = mainLayout.initialize(document.getElementById('app'));
    
    // Create chat panel
    chatPanel = new ChatPanel();
    chatPanel.initialize(chatContainer);
    
    // Set up event listeners
    setupEventListeners();
    
    // Check Ollama status
    const ollamaStatus = await api.getOllamaStatus();
    handleOllamaStatus(ollamaStatus);
    
    console.log('CodeLve initialized successfully');
  } catch (error) {
    console.error('Error initializing CodeLve:', error);
    showErrorMessage('Failed to initialize application. Please check the logs for details.');
  }
}

/**
 * Set up event listeners for UI components
 */
function setupEventListeners() {
  // Listen for chat messages
  chatPanel.on('message', async (message) => {
    const context = codeContextProvider.getContext();
    
    try {
      const response = await api.queryAI({ prompt: message, context });
      chatPanel.handleAIResponse(response);
    } catch (error) {
      console.error('Error querying AI:', error);
      chatPanel.addSystemMessage(`Error: Failed to get response from AI. ${error.message}`);
    }
  });
  
  // Listen for file selection
  document.addEventListener('file-selected', (event) => {
    const { filePath, content } = event.detail;
    codeContextProvider.setActiveFile(filePath, content);
  });
  
  // Listen for project/workspace selection
  document.addEventListener('project-selected', (event) => {
    const { projectPath } = event.detail;
    codeContextProvider.setActiveProject(projectPath);
  });
  
  // Listen for theme changes
  document.addEventListener('theme-changed', (event) => {
    const { isDark } = event.detail;
    document.body.classList.toggle('theme-dark', isDark);
  });
}

/**
 * Handle the status of the Ollama service
 * 
 * @param {Object} status Ollama status object
 */
function handleOllamaStatus(status) {
  if (!status.running) {
    chatPanel.addSystemMessage('Ollama service is not running. Some features may not be available.');
    return;
  }
  
  if (!status.modelAvailable) {
    chatPanel.addSystemMessage(`Model ${status.modelName} is not available. Please install it through the settings panel.`);
    return;
  }
  
  if (status.ready) {
    chatPanel.addSystemMessage(`Connected to AI assistant (${status.modelName}). How can I help you with your code today?`);
  } else {
    chatPanel.addSystemMessage(`AI service is initializing. Please wait a moment.`);
  }
}

/**
 * Show error message to the user
 * 
 * @param {string} message Error message
 */
function showErrorMessage(message) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.textContent = message;
  document.body.appendChild(errorDiv);
}

/**
 * Application cleanup on window unload
 */
function cleanup() {
  if (codeContextProvider) {
    codeContextProvider.cleanup();
  }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);

// Clean up when the window is closed
window.addEventListener('beforeunload', cleanup);