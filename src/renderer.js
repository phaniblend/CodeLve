/**
 * Renderer process entry point for CodeLve
 * 
 * Initializes the user interface and connects it to the backend services
 */

// UI component instances
let mainLayout;
let chatPanel;
let codeContextProvider;

// Window control handlers
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('minimize-button')?.addEventListener('click', () => {
    if (window.api && window.api.minimizeWindow) {
      window.api.minimizeWindow();
    } else {
      console.error('Window API not available');
    }
  });
  
  document.getElementById('maximize-button')?.addEventListener('click', () => {
    if (window.api && window.api.maximizeWindow) {
      window.api.maximizeWindow();
    } else {
      console.error('Window API not available');
    }
  });
  
  document.getElementById('close-button')?.addEventListener('click', () => {
    if (window.api && window.api.closeWindow) {
      window.api.closeWindow();
    } else {
      console.error('Window API not available');
    }
  });
  
  document.getElementById('settings-button')?.addEventListener('click', () => {
    // Will implement settings panel later
    console.log('Settings button clicked');
  });
  
  // Initialize the application
  initializeApp();
});

/**
 * Initialize the application UI
 */
async function initializeApp() {
  try {
    // Check if appInfo is available
    const version = window.appInfo ? window.appInfo.version : '0.1.0';
    console.log(`Initializing CodeLve v${version}`);
    
    // Handle UI modules once they're implemented
    // For now, we'll just show a message
    showErrorMessage('UI components not yet implemented. This is a basic shell.');
    
    console.log('CodeLve basic shell initialized');
  } catch (error) {
    console.error('Error initializing CodeLve:', error);
    showErrorMessage('Failed to initialize application. Please check the logs for details.');
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