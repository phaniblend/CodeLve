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
 * Initialize the CodeLve Editor
 * 
 * @param {Element} container Editor container
 */
async function initializeCodeLveEditor(container) {
  try {
    // Clear the container
    container.innerHTML = '';
    
    // Create a simple code editor that works in the browser

    // Layout - Split panel with explorer and editor
    const editorLayout = document.createElement('div');
    editorLayout.className = 'code-editor-layout';
    editorLayout.style.display = 'flex';
    editorLayout.style.width = '100%';
    editorLayout.style.height = '100%';
    editorLayout.style.backgroundColor = '#1e1e2e';
    editorLayout.style.color = '#cdd6f4';
    container.appendChild(editorLayout);
    
    // File explorer panel
    const explorerPanel = document.createElement('div');
    explorerPanel.className = 'explorer-container';
    explorerPanel.style.width = '250px';
    explorerPanel.style.minWidth = '150px';
    explorerPanel.style.maxWidth = '400px';
    explorerPanel.style.height = '100%';
    explorerPanel.style.borderRight = '1px solid #313244';
    explorerPanel.style.overflow = 'hidden';
    explorerPanel.style.display = 'flex';
    explorerPanel.style.flexDirection = 'column';
    editorLayout.appendChild(explorerPanel);
    
    // Resize handle
    const resizeHandle = document.createElement('div');
    resizeHandle.className = 'resize-handle-vertical';
    resizeHandle.style.width = '5px';
    resizeHandle.style.height = '100%';
    resizeHandle.style.backgroundColor = '#181825';
    resizeHandle.style.cursor = 'ew-resize';
    editorLayout.appendChild(resizeHandle);
    
    // Editor panel
    const editorPanel = document.createElement('div');
    editorPanel.className = 'editor-container';
    editorPanel.style.flex = '1';
    editorPanel.style.height = '100%';
    editorPanel.style.display = 'flex';
    editorPanel.style.flexDirection = 'column';
    editorLayout.appendChild(editorPanel);
    
    // Explorer header
    const explorerHeader = document.createElement('div');
    explorerHeader.className = 'explorer-header';
    explorerHeader.style.display = 'flex';
    explorerHeader.style.alignItems = 'center';
    explorerHeader.style.justifyContent = 'space-between';
    explorerHeader.style.padding = '8px 12px';
    explorerHeader.style.borderBottom = '1px solid #313244';
    explorerHeader.innerHTML = `
      <div class="explorer-title" style="font-weight: bold;">Explorer</div>
      <div class="explorer-actions">
        <button id="open-folder-btn" class="explorer-action" style="background: none; border: none; cursor: pointer; font-size: 16px; color: #cdd6f4;">📂</button>
        <button id="refresh-btn" class="explorer-action" style="background: none; border: none; cursor: pointer; font-size: 16px; color: #cdd6f4;">🔄</button>
        <button id="new-file-btn" class="explorer-action" style="background: none; border: none; cursor: pointer; font-size: 16px; color: #cdd6f4;">📄</button>
      </div>
    `;
    explorerPanel.appendChild(explorerHeader);
    
    // Explorer content
    const explorerContent = document.createElement('div');
    explorerContent.className = 'explorer-content';
    explorerContent.style.flex = '1';
    explorerContent.style.overflow = 'auto';
    explorerContent.style.padding = '8px 0';
    explorerContent.innerHTML = '<div class="explorer-placeholder" style="padding: 16px; text-align: center; color: #6c7086;">No folder opened. Click the folder icon to open a project.</div>';
    explorerPanel.appendChild(explorerContent);
    
    // Editor content
    const editorContent = document.createElement('div');
    editorContent.className = 'editor-content';
    editorContent.style.flex = '1';
    editorContent.style.position = 'relative';
    editorPanel.appendChild(editorContent);
    
    // Editor placeholder
    const editorPlaceholder = document.createElement('div');
    editorPlaceholder.className = 'editor-placeholder';
    editorPlaceholder.style.position = 'absolute';
    editorPlaceholder.style.top = '50%';
    editorPlaceholder.style.left = '50%';
    editorPlaceholder.style.transform = 'translate(-50%, -50%)';
    editorPlaceholder.style.textAlign = 'center';
    editorPlaceholder.style.color = '#6c7086';
    editorPlaceholder.style.padding = '20px';
    editorPlaceholder.innerHTML = 'No file selected. Open a file using the Explorer.';
    editorContent.appendChild(editorPlaceholder);
    
    // Create a textarea for editing (hidden initially)
    const editorTextarea = document.createElement('textarea');
    editorTextarea.className = 'editor-textarea';
    editorTextarea.style.width = '100%';
    editorTextarea.style.height = '100%';
    editorTextarea.style.padding = '12px';
    editorTextarea.style.margin = '0';
    editorTextarea.style.border = 'none';
    editorTextarea.style.fontFamily = 'monospace';
    editorTextarea.style.fontSize = '14px';
    editorTextarea.style.lineHeight = '1.5';
    editorTextarea.style.backgroundColor = '#1e1e2e';
    editorTextarea.style.color = '#cdd6f4';
    editorTextarea.style.resize = 'none';
    editorTextarea.style.outline = 'none';
    editorTextarea.style.display = 'none';
    editorContent.appendChild(editorTextarea);
    
    // Editor statusbar
    const statusBar = document.createElement('div');
    statusBar.className = 'editor-statusbar';
    statusBar.style.height = '24px';
    statusBar.style.display = 'flex';
    statusBar.style.alignItems = 'center';
    statusBar.style.padding = '0 12px';
    statusBar.style.fontSize = '12px';
    statusBar.style.color = '#a6adc8';
    statusBar.style.backgroundColor = '#181825';
    statusBar.style.borderTop = '1px solid #313244';
    statusBar.innerHTML = '<div>Ready</div>';
    editorPanel.appendChild(statusBar);
    
    // Setup resize functionality
    setupResizeHandler(resizeHandle, explorerPanel);
    
    // Track state
    const editorState = {
      currentFolder: null,
      currentFile: null,
      files: new Map(), // Map of file paths to contents
      modified: new Set() // Set of modified file paths
    };
    
    // Setup event handlers
    document.getElementById('open-folder-btn').addEventListener('click', async () => {
      if (!window.api || !window.api.showOpenDialog) {
        showEditorError('The file system API is not available.');
        return;
      }
      
      try {
        const result = await window.api.showOpenDialog({
          properties: ['openDirectory']
        });
        
        if (!result.canceled && result.filePaths && result.filePaths.length > 0) {
          await loadFolder(result.filePaths[0], explorerContent, editorState);
        }
      } catch (error) {
        showEditorError(`Error opening folder: ${error.message}`);
      }
    });
    
    document.getElementById('refresh-btn').addEventListener('click', async () => {
      if (editorState.currentFolder) {
        await loadFolder(editorState.currentFolder, explorerContent, editorState);
      }
    });
    
    document.getElementById('new-file-btn').addEventListener('click', async () => {
      if (!editorState.currentFolder) {
        showEditorError('Please open a folder first.');
        return;
      }
      
      const fileName = prompt('Enter file name:');
      if (!fileName) return;
      
      try {
        const filePath = await createNewFile(editorState.currentFolder, fileName);
        
        // Refresh folder
        await loadFolder(editorState.currentFolder, explorerContent, editorState);
        
        // Open the new file
        await openFile(filePath, editorTextarea, editorPlaceholder, statusBar, editorState);
      } catch (error) {
        showEditorError(`Error creating file: ${error.message}`);
      }
    });
    
    // Add change detection to textarea
    editorTextarea.addEventListener('input', () => {
      if (editorState.currentFile) {
        // Update file content
        editorState.files.set(editorState.currentFile, editorTextarea.value);
        editorState.modified.add(editorState.currentFile);
        
        // Auto-save
        saveFile(editorState.currentFile, editorTextarea.value, statusBar, editorState);
        
        // Update context for AI
        if (typeof codeContextProvider !== 'undefined' && codeContextProvider !== null) {
          codeContextProvider.setActiveFile(editorState.currentFile, editorTextarea.value);
        }
      }
    });
    
    // Store reference to the editor for later use
    window.codeEditor = {
      state: editorState,
      openFolder: (path) => loadFolder(path, explorerContent, editorState),
      openFile: (path) => openFile(path, editorTextarea, editorPlaceholder, statusBar, editorState),
      getContent: () => editorState.currentFile ? editorState.files.get(editorState.currentFile) : null,
      getContext: () => {
        if (!editorState.currentFile) return null;
        
        return {
          path: editorState.currentFile,
          content: editorState.files.get(editorState.currentFile),
          language: getFileExtension(editorState.currentFile)
        };
      }
    };
    
    // Update editor status indicators
    const ideIndicator = document.getElementById("ide-status-indicator");
    const ideText = document.getElementById("ide-status-text");

    if (ideIndicator && ideText) {
      ideIndicator.className = "status-indicator online";
      ideText.textContent = "CodeLve Editor active";
    }
    
    // Success message in status bar
    statusBar.innerHTML = '<div>Editor initialized successfully</div>';
    
  } catch (error) {
    console.error('Error initializing CodeLve Editor:', error);
    
    // Show error message in the editor container
    container.innerHTML = `
      <div style="padding: 20px; color: #f38ba8; text-align: center;">
        <h3>Error Initializing Editor</h3>
        <p>${error.message || 'Unknown error'}</p>
        <button onclick="location.reload()">Retry</button>
      </div>
    `;
    
    // Update status indicators
    const ideIndicator = document.getElementById("ide-status-indicator");
    const ideText = document.getElementById("ide-status-text");
    
    if (ideIndicator && ideText) {
      ideIndicator.className = "status-indicator error";
      ideText.textContent = "Editor error";
    }
  }
}

/**
 * Setup resize handler for the explorer panel
 * 
 * @param {Element} handle Resize handle element
 * @param {Element} panel Panel to resize
 */
function setupResizeHandler(handle, panel) {
  let isResizing = false;
  let startX = 0;
  let startWidth = 0;
  
  handle.addEventListener('mousedown', (e) => {
    isResizing = true;
    startX = e.clientX;
    startWidth = panel.offsetWidth;
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'ew-resize';
  });
  
  document.addEventListener('mousemove', (e) => {
    if (!isResizing) return;
    
    const dx = e.clientX - startX;
    const newWidth = Math.max(150, Math.min(400, startWidth + dx));
    panel.style.width = `${newWidth}px`;
  });
  
  document.addEventListener('mouseup', () => {
    if (isResizing) {
      isResizing = false;
      document.body.style.userSelect = '';
      document.body.style.cursor = '';
    }
  });
}

/**
 * Load a folder into the explorer
 * 
 * @param {string} folderPath Folder path
 * @param {Element} explorerContent Explorer content element
 * @param {Object} editorState Editor state
 */
async function loadFolder(folderPath, explorerContent, editorState) {
  if (!window.api || !window.api.listDirectory) {
    showEditorError('The file system API is not available.');
    return;
  }
  
  try {
    // List directory contents
    const items = await window.api.listDirectory(folderPath);
    
    // Set current folder
    editorState.currentFolder = folderPath;
    
    // Clear explorer content
    explorerContent.innerHTML = '';
    
    // Add folder path display
    const pathDisplay = document.createElement('div');
    pathDisplay.className = 'path-display';
    pathDisplay.style.fontSize = '11px';
    pathDisplay.style.padding = '4px 8px';
    pathDisplay.style.color = '#6c7086';
    pathDisplay.style.borderBottom = '1px solid #313244';
    pathDisplay.style.whiteSpace = 'nowrap';
    pathDisplay.style.overflow = 'hidden';
    pathDisplay.style.textOverflow = 'ellipsis';
    pathDisplay.style.marginBottom = '4px';
    pathDisplay.textContent = folderPath;
    explorerContent.appendChild(pathDisplay);
    
    // Sort items: directories first, then files
    items.sort((a, b) => {
      if (a.isDirectory && !b.isDirectory) return -1;
      if (!a.isDirectory && b.isDirectory) return 1;
      return a.name.localeCompare(b.name);
    });
    
    // Add items to explorer
    for (const item of items) {
      const itemElement = document.createElement('div');
      itemElement.className = 'file-item';
      itemElement.style.padding = '4px 8px';
      itemElement.style.cursor = 'pointer';
      itemElement.style.display = 'flex';
      itemElement.style.alignItems = 'center';
      itemElement.style.borderRadius = '4px';
      itemElement.style.margin = '2px 4px';
      
      const icon = document.createElement('span');
      icon.className = 'item-icon';
      icon.style.marginRight = '6px';
      icon.textContent = item.isDirectory ? '📁' : '📄';
      
      const name = document.createElement('span');
      name.className = 'item-name';
      name.style.flex = '1';
      name.style.whiteSpace = 'nowrap';
      name.style.overflow = 'hidden';
      name.style.textOverflow = 'ellipsis';
      name.textContent = item.name;
      
      itemElement.appendChild(icon);
      itemElement.appendChild(name);
      
      // Add hover effect
      itemElement.addEventListener('mouseover', () => {
        itemElement.style.backgroundColor = '#313244';
      });
      
      itemElement.addEventListener('mouseout', () => {
        itemElement.style.backgroundColor = '';
      });
      
      // Add click handler
      itemElement.addEventListener('click', async (e) => {
        if (item.isDirectory) {
          // Open subfolder
          await loadFolder(item.path, explorerContent, editorState);
        } else {
          // Select this item
          const fileItems = explorerContent.querySelectorAll('.file-item');
          fileItems.forEach(el => {
            el.style.backgroundColor = '';
            el.classList.remove('selected');
          });
          
          itemElement.classList.add('selected');
          itemElement.style.backgroundColor = '#45475a';
          
          // Open file
          await openFile(item.path, document.querySelector('.editor-textarea'), 
                         document.querySelector('.editor-placeholder'),
                         document.querySelector('.editor-statusbar'),
                         editorState);
        }
      });
      
      explorerContent.appendChild(itemElement);
    }
  } catch (error) {
    showEditorError(`Error loading folder: ${error.message}`);
  }
}

/**
 * Open a file in the editor
 * 
 * @param {string} filePath File path
 * @param {Element} textarea Editor textarea
 * @param {Element} placeholder Editor placeholder
 * @param {Element} statusBar Status bar
 * @param {Object} editorState Editor state
 */
async function openFile(filePath, textarea, placeholder, statusBar, editorState) {
  if (!window.api || !window.api.readFile) {
    showEditorError('The file system API is not available.');
    return;
  }
  
  try {
    // Load file if not already loaded
    let content = editorState.files.get(filePath);
    
    if (content === undefined) {
      content = await window.api.readFile(filePath);
      editorState.files.set(filePath, content);
    }
    
    // Set the current file
    editorState.currentFile = filePath;
    
    // Show content in editor
    textarea.value = content;
    textarea.style.display = 'block';
    placeholder.style.display = 'none';
    
    // Apply syntax highlighting (basic)
    // syntaxHighlight(textarea, getFileExtension(filePath));
    
    // Update status bar
    updateStatusBar(statusBar, filePath);
    
    // Focus editor
    textarea.focus();
    
    // Update context for AI
    if (typeof codeContextProvider !== 'undefined' && codeContextProvider !== null) {
      codeContextProvider.setActiveFile(filePath, content);
    }
  } catch (error) {
    showEditorError(`Error opening file: ${error.message}`);
  }
}

/**
 * Save the current file
 * 
 * @param {string} filePath File path
 * @param {string} content File content
 * @param {Element} statusBar Status bar
 * @param {Object} editorState Editor state
 */
async function saveFile(filePath, content, statusBar, editorState) {
  if (!window.api || !window.api.writeFile) {
    showEditorError('The file system API is not available.');
    return;
  }
  
  try {
    await window.api.writeFile(filePath, content);
    editorState.modified.delete(filePath);
    
    // Update status bar with saved indication
    updateStatusBar(statusBar, filePath, 'Saved');
    
    // Fade out the "Saved" indicator after 2 seconds
    setTimeout(() => {
      updateStatusBar(statusBar, filePath);
    }, 2000);
  } catch (error) {
    showEditorError(`Error saving file: ${error.message}`);
  }
}

/**
 * Create a new file
 * 
 * @param {string} folderPath Folder path
 * @param {string} fileName File name
 * @returns {Promise<string>} File path
 */
async function createNewFile(folderPath, fileName) {
  if (!window.api || !window.api.writeFile) {
    throw new Error('The file system API is not available.');
  }
  
  // Construct file path
  const filePath = `${folderPath}/${fileName}`;
  
  try {
    // Check if file exists
    try {
      await window.api.readFile(filePath);
      throw new Error(`File "${fileName}" already exists.`);
    } catch (err) {
      // File doesn't exist, which is what we want
    }
    
    // Create empty file
    await window.api.writeFile(filePath, '');
    
    return filePath;
  } catch (error) {
    throw error;
  }
}

/**
 * Update the status bar
 * 
 * @param {Element} statusBar Status bar element
 * @param {string} filePath Current file path
 * @param {string} status Status message (optional)
 */
function updateStatusBar(statusBar, filePath, status = null) {
  if (!statusBar) return;
  
  const fileName = filePath.split(/[\/\\]/).pop();
  const extension = getFileExtension(filePath);
  
  statusBar.innerHTML = `
    <div style="display: flex; justify-content: space-between; width: 100%;">
      <div>${fileName} ${status ? `- ${status}` : ''}</div>
      <div>${extension.toUpperCase()}</div>
    </div>
  `;
}

/**
 * Get file extension
 * 
 * @param {string} filePath File path
 * @returns {string} File extension
 */
function getFileExtension(filePath) {
  return filePath.split('.').pop().toLowerCase();
}

/**
 * Show an error message in the editor
 * 
 * @param {string} message Error message
 */
function showEditorError(message) {
  console.error(`Editor error: ${message}`);
  
  const statusBar = document.querySelector('.editor-statusbar');
  if (statusBar) {
    statusBar.innerHTML = `<div style="color: #f38ba8;">Error: ${message}</div>`;
  }
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
      The integrated editor component is not active yet.
      Click the button below to initialize the CodeLve Editor.
    </p>
    <button class="editor-placeholder-button" id="init-editor-button">
      Initialize CodeLve Editor
    </button>
  `;

  container.appendChild(placeholder);

  // Add event listener for initialize button
  document
    .getElementById("init-editor-button")
    ?.addEventListener("click", () => {
      initializeCodeLveEditor(container);
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