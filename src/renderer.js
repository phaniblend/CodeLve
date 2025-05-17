/**
 * Simple code context provider for testing
 */
class CodeContextProvider {
  constructor() {
    this.context = '';
  }
  
  /**
   * Get context for the AI
   * @returns {string} Context string
   */
  getContext() {
    // For testing, return a sample file with content
    return 'File: test.js\nPath: /test.js\nType: js\n\n```js\n// Sample code for testing\nfunction hello() {\n  console.log("Hello, world!");\n}\n```';
  }
}
/**
 * Renderer process entry point for CodeLve
 *
 * Initializes the user interface and connects it to the backend services
 */

// UI component instances
let mainLayout = null;
let chatPanel = null;

// Window control handlers
document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded, setting up window controls");

  // Setup window controls
  document.getElementById("minimize-button")?.addEventListener("click", () => {
    if (window.api && window.api.minimizeWindow) {
      window.api.minimizeWindow();
    } else {
      console.error("Window API not available");
    }
  });

  document.getElementById("maximize-button")?.addEventListener("click", () => {
    if (window.api && window.api.maximizeWindow) {
      window.api.maximizeWindow();
    } else {
      console.error("Window API not available");
    }
  });

  document.getElementById("close-button")?.addEventListener("click", () => {
    if (window.api && window.api.closeWindow) {
      window.api.closeWindow();
    } else {
      console.error("Window API not available");
    }
  });

  document.getElementById("settings-button")?.addEventListener("click", () => {
    // Will implement settings panel later
    console.log("Settings button clicked");
  });

  // Initialize the application
  initializeApp();
});

/**
 * Initialize application components
 */
async function initializeApp() {
  try {
    console.log("Starting CodeLve...");

    // Initialize code context provider
    codeContextProvider = new CodeContextProvider();
    
    // AI service is initialized in the main process
    // We'll interact with it through IPC

    // IDE integration is disabled for now while we focus on AI functionality
    console.log("Lite XL integration disabled for testing, running in AI-only mode");
    let ideAvailable = false;

    // Create main window
    createMainWindow();

    // Setup IPC handlers
    setupIPCHandlers();

    console.log("CodeLve started successfully");
  } catch (error) {
    console.error("Error initializing CodeLve:", error);
    if (window.api && window.api.closeWindow) {
      window.api.closeWindow();
    } else {
      console.error('Unable to close window through API');
    }
  }
}

/**
 * Update AI service status
 */
async function updateAIStatus() {
  // Try new API name first, fall back to old one for compatibility
  const statusApi = window.api?.getAIStatus || window.api?.getOllamaStatus;
  
  if (window.api && statusApi) {
    try {
      const status = await statusApi();
      updateStatusIndicators(status);
      
      // If not ready, check again in 5 seconds
      if (status && !status.ready) {
        setTimeout(updateAIStatus, 5000);
      }
    } catch (error) {
      console.error("Error checking AI status:", error);
      updateStatusIndicators({ running: false, error: error.message });
    }
  } else {
    updateStatusIndicators({ running: false, error: "API not available" });
  }
}

/**
 * Setup IPC handlers for renderer-to-main communication
 */
function setupIPCHandlers() {
  console.log("Setting up IPC handlers");
  
}

function createMainWindow() {
  console.log("Creating main window components");

  // Create and setup the main layout
  createMainLayout();

  // Setup the chat panel
  setupChatPanel();

  // Check AI service status and update indicators
  updateAIStatus();
}

/**
 * Create editor placeholder when Lite XL is not available
 *
 * @param {Element} container Editor container element
 */
function createEditorPlaceholder(container) {
  const placeholder = document.createElement("div");
  placeholder.className = "editor-placeholder";

  placeholder.innerHTML = `
    <div class="editor-placeholder-icon">📝</div>
    <h2 class="editor-placeholder-title">Editor Not Available</h2>
    <p class="editor-placeholder-text">
      The integrated editor component is not available. 
      CodeLve works best with Lite XL installed. 
      You can still use the AI assistant to answer questions and generate code.
    </p>
    <button class="editor-placeholder-button" id="install-editor-button">
      Install Lite XL
    </button>
  `;

  container.appendChild(placeholder);

  // Add event listener for install button
  document
    .getElementById("install-editor-button")
    ?.addEventListener("click", () => {
      if (window.api && window.api.openExternal) {
        window.api.openExternal("https://lite-xl.com/");
      } else {
        window.open("https://lite-xl.com/", "_blank");
      }
    });
}

/**
 * Create and setup the main layout
 */
function createMainLayout() {
  const appContainer = document.getElementById("app");
  if (!appContainer) {
    console.error("App container not found");
    return;
  }

  // Make app container flex
  appContainer.style.display = "flex";
  appContainer.style.flexDirection = "row";
  appContainer.style.width = "100%";
  appContainer.style.height = "100%";
  appContainer.style.overflow = "hidden";

  // Create layout containers
  const editorContainer = document.createElement("div");
  editorContainer.className = "editor-container";
  editorContainer.style.flex = "6"; // 60% of space

  const resizeHandle = document.createElement("div");
  resizeHandle.className = "resize-handle";

  const chatContainer = document.createElement("div");
  chatContainer.className = "chat-container";
  chatContainer.style.flex = "4"; // 40% of space

  // Add to DOM
  appContainer.appendChild(editorContainer);
  appContainer.appendChild(resizeHandle);
  appContainer.appendChild(chatContainer);

  // Add editor placeholder
  createEditorPlaceholder(editorContainer);

  // Setup resize functionality
  let isDragging = false;
  let startX = 0;
  let initialEditorFlex = 6;
  let initialChatFlex = 4;

  resizeHandle.addEventListener("mousedown", (e) => {
    isDragging = true;
    startX = e.clientX;
    initialEditorFlex =
      parseFloat(window.getComputedStyle(editorContainer).flexGrow) || 6;
    initialChatFlex =
      parseFloat(window.getComputedStyle(chatContainer).flexGrow) || 4;
    resizeHandle.classList.add("dragging");

    // Prevent text selection during drag
    document.body.style.userSelect = "none";
  });

  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;

    const containerWidth = appContainer.clientWidth;
    const deltaX = e.clientX - startX;
    const deltaRatio = deltaX / containerWidth;

    // Calculate new flex values (min 2, max 8)
    const newEditorFlex = Math.max(
      2,
      Math.min(8, initialEditorFlex + deltaRatio * 10)
    );
    const newChatFlex = Math.max(
      2,
      Math.min(8, initialChatFlex - deltaRatio * 10)
    );

    // Apply new flex values
    editorContainer.style.flex = newEditorFlex;
    chatContainer.style.flex = newChatFlex;
  });

  document.addEventListener("mouseup", () => {
    if (isDragging) {
      isDragging = false;
      resizeHandle.classList.remove("dragging");
      document.body.style.userSelect = "";
    }
  });

  // Save reference to containers
  mainLayout = {
    editorContainer,
    chatContainer,
    resizeHandle,
  };
}

/**
 * Setup the chat panel
 */
function setupChatPanel() {
  if (!mainLayout || !mainLayout.chatContainer) {
    console.error("Layout not initialized");
    return;
  }

  const container = mainLayout.chatContainer;

  // Create panel elements
  const panel = document.createElement("div");
  panel.className = "chat-panel";

  // Create messages container
  const messagesContainer = document.createElement("div");
  messagesContainer.className = "messages-container";
  panel.appendChild(messagesContainer);

  // Create input area
  const inputContainer = document.createElement("div");
  inputContainer.className = "input-container";

  const textarea = document.createElement("textarea");
  textarea.className = "chat-input";
  textarea.placeholder = "Ask about your code...";
  textarea.rows = 3;

  const sendButton = document.createElement("button");
  sendButton.className = "send-button";
  sendButton.textContent = "Send";

  // Add event listeners
  sendButton.addEventListener("click", () => {
    sendMessage(textarea.value);
  });

  textarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(textarea.value);
    }
  });

  // Append elements
  inputContainer.appendChild(textarea);
  inputContainer.appendChild(sendButton);
  panel.appendChild(inputContainer);

  // Append panel to container
  container.appendChild(panel);

  // Add welcome message
  addSystemMessage(
    messagesContainer,
    "Welcome to CodeLve! Ask me anything about your code or how to implement new features."
  );

  // Save reference to chat panel
  chatPanel = {
    panel,
    messagesContainer,
    textarea,
    sendButton,
  };
}

/**
 * Send a message to the AI
 *
 * @param {string} content Message content
 */
async function sendMessage(content) {
  if (!content || !content.trim() || !chatPanel) return;

  const { messagesContainer, textarea } = chatPanel;

  // Add user message
  addUserMessage(messagesContainer, content);

  // Clear input
  textarea.value = "";

  // Add loading message
  const loadingId = addLoadingMessage(messagesContainer);

  // Send to AI if API available
  if (window.api && window.api.queryAI) {
    try {
      // Get code context if available
      let codeContext = '';
      if (codeContextProvider) {
        codeContext = codeContextProvider.getContext();
        console.log('Including code context in AI query:', 
          codeContext ? `${codeContext.length} characters` : 'none');
      }
      
      const response = await window.api.queryAI({ 
        prompt: content, 
        context: codeContext 
      });
      
      // Remove loading message
      removeMessage(messagesContainer, loadingId);
      
      if (response.error) {
        addSystemMessage(messagesContainer, `Error: ${response.error}`);
      } else if (response.response) {
        addAIMessage(messagesContainer, response.response);
      } else {
        addSystemMessage(messagesContainer, 'Received empty response from AI.');
      }
    } catch (error) {
      // Remove loading message
      removeMessage(messagesContainer, loadingId);
      addSystemMessage(messagesContainer, `Error: Failed to get AI response. ${error.message || ''}`);
      console.error('Error querying AI:', error);
    }
  } else {
    // Remove loading message
    removeMessage(messagesContainer, loadingId);
    addSystemMessage(
      messagesContainer,
      "AI service not available. Please check if the AI server is installed and running."
    );
  }
}

/**
 * Add a user message to the chat
 *
 * @param {Element} container Messages container
 * @param {string} content Message content
 */
function addUserMessage(container, content) {
  const messageEl = document.createElement("div");
  messageEl.className = "message user-message";

  const time = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  messageEl.innerHTML = `
    <div class="message-header">
      <span class="message-sender">You</span>
      <span class="message-time">${time}</span>
    </div>
    <div class="message-content">${escapeHTML(content)}</div>
  `;

  container.appendChild(messageEl);
  scrollToBottom(container);
}

/**
 * Add an AI message to the chat
 *
 * @param {Element} container Messages container
 * @param {string} content Message content
 */
function addAIMessage(container, content) {
  const messageEl = document.createElement("div");
  messageEl.className = "message ai-message";

  const time = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  // Process code blocks
  const processedContent = processCodeBlocks(content);

  messageEl.innerHTML = `
    <div class="message-header">
      <span class="message-sender">CodeLve</span>
      <span class="message-time">${time}</span>
    </div>
    <div class="message-content">${processedContent}</div>
  `;

  container.appendChild(messageEl);
  scrollToBottom(container);
}

/**
 * Add a system message to the chat
 *
 * @param {Element} container Messages container
 * @param {string} content Message content
 */
function addSystemMessage(container, content) {
  const messageEl = document.createElement("div");
  messageEl.className = "message system-message";

  const time = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  messageEl.innerHTML = `
    <div class="message-header">
      <span class="message-sender">System</span>
      <span class="message-time">${time}</span>
    </div>
    <div class="message-content">${escapeHTML(content)}</div>
  `;

  container.appendChild(messageEl);
  scrollToBottom(container);
}

/**
 * Add a loading message to the chat
 *
 * @param {Element} container Messages container
 * @returns {string} Message ID
 */
function addLoadingMessage(container) {
  const id = "loading-" + Date.now();
  const loadingEl = document.createElement("div");
  loadingEl.className = "message loading-message";
  loadingEl.id = id;

  loadingEl.innerHTML = `
    <div class="message-content">
      <div class="loading-indicator">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
      <div class="loading-text">Thinking...</div>
    </div>
  `;

  container.appendChild(loadingEl);
  scrollToBottom(container);

  return id;
}

/**
 * Remove a message from the chat
 *
 * @param {Element} container Messages container
 * @param {string} id Message ID
 */
function removeMessage(container, id) {
  const messageEl = document.getElementById(id);
  if (messageEl) {
    messageEl.remove();
  }
}

/**
 * Process code blocks in message content
 *
 * @param {string} content Message content
 * @returns {string} Processed content
 */
function processCodeBlocks(content) {
  // Replace code blocks with styled elements
  return content.replace(
    /```([\w]*)\n([\s\S]*?)```/g,
    (match, language, code) => {
      const langClass = language ? ` language-${language}` : "";
      return `<pre class="code-block${langClass}"><code>${escapeHTML(
        code
      )}</code></pre>`;
    }
  );
}

/**
 * Escape HTML in text
 *
 * @param {string} html HTML string
 * @returns {string} Escaped HTML
 */
function escapeHTML(html) {
  const div = document.createElement("div");
  div.textContent = html;
  return div.innerHTML;
}

/**
 * Scroll to the bottom of the container
 *
 * @param {Element} container Container element
 */
function scrollToBottom(container) {
  container.scrollTop = container.scrollHeight;
}

/**
 * Update status indicators based on service status
 *
 * @param {Object} status Status object
 */
function updateStatusIndicators(status) {
  // Update AI status
  const aiIndicator = document.getElementById("ai-status-indicator");
  const aiText = document.getElementById("ai-status-text");

  if (aiIndicator && aiText) {
    if (status && status.running) {
      if (status.ready) {
        aiIndicator.className = "status-indicator online";
        aiText.textContent = `AI ready (${status.modelName})`;
      } else {
        aiIndicator.className = "status-indicator loading";
        aiText.textContent = "AI initializing...";
      }
    } else {
      aiIndicator.className = "status-indicator offline";
      aiText.textContent = "AI service not available";
    }
  }

  // Update IDE status (for now, just show as offline)
  const ideIndicator = document.getElementById("ide-status-indicator");
  const ideText = document.getElementById("ide-status-text");

  if (ideIndicator && ideText) {
    ideIndicator.className = "status-indicator offline";
    ideText.textContent = "Lite XL not connected";
  }
}

/**
 * Show error message to the user
 *
 * @param {string} message Error message
 */
function showErrorMessage(message) {
  const errorDiv = document.createElement("div");
  errorDiv.className = "error-message";
  errorDiv.textContent = message;
  document.body.appendChild(errorDiv);
}