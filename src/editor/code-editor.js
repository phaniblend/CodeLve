/**
 * Code Editor Integration for CodeLve
 * 
 * Combines file explorer with Ace Editor
 */

const AceEditor = require('./ace-editor');
const FileExplorer = require('./file-explorer');
const fs = require('fs');
const path = require('path');
const EventEmitter = require('events');

class CodeEditor extends EventEmitter {
  constructor() {
    super();
    this.container = null;
    this.isInitialized = false;
    this.fileExplorer = new FileExplorer();
    this.aceEditor = new AceEditor();
    this.currentFile = null;
  }

  /**
   * Initialize the Code Editor
   * 
   * @param {Element} container The container element
   * @returns {void}
   */
  initialize(container) {
    if (this.isInitialized) return;

    this.container = container;
    
    // Create layout
    this.createLayout();
    
    // Initialize components
    this.fileExplorer.initialize(this.explorerContainer);
    this.aceEditor.initialize(this.editorContainer, this.handleEditorChange.bind(this));
    
    // Setup event listeners
    this.setupEventListeners();
    
    this.isInitialized = true;
  }

  /**
   * Create the layout
   */
  createLayout() {
    // Clear container
    this.container.innerHTML = '';
    
    // Create layout
    const layout = document.createElement('div');
    layout.className = 'code-editor-layout';
    layout.style.display = 'flex';
    layout.style.width = '100%';
    layout.style.height = '100%';
    
    // Create explorer container
    this.explorerContainer = document.createElement('div');
    this.explorerContainer.className = 'explorer-container';
    this.explorerContainer.style.width = '250px';
    this.explorerContainer.style.height = '100%';
    this.explorerContainer.style.overflow = 'auto';
    this.explorerContainer.style.borderRight = '1px solid #ccc';
    
    // Create editor container
    this.editorContainer = document.createElement('div');
    this.editorContainer.className = 'editor-container';
    this.editorContainer.style.flex = '1';
    this.editorContainer.style.height = '100%';
    
    // Create resize handle
    this.resizeHandle = document.createElement('div');
    this.resizeHandle.className = 'resize-handle-vertical';
    this.resizeHandle.style.width = '5px';
    this.resizeHandle.style.height = '100%';
    this.resizeHandle.style.backgroundColor = '#ccc';
    this.resizeHandle.style.cursor = 'ew-resize';
    
    // Add to layout
    layout.appendChild(this.explorerContainer);
    layout.appendChild(this.resizeHandle);
    layout.appendChild(this.editorContainer);
    
    // Add to container
    this.container.appendChild(layout);
    
    // Setup resize functionality
    this.setupResize();
  }

  /**
   * Setup resize functionality
   */
  setupResize() {
    let isResizing = false;
    let startX = 0;
    let startWidth = 0;
    
    this.resizeHandle.addEventListener('mousedown', (e) => {
      isResizing = true;
      startX = e.clientX;
      startWidth = this.explorerContainer.offsetWidth;
      
      // Prevent text selection during resize
      document.body.style.userSelect = 'none';
    });
    
    document.addEventListener('mousemove', (e) => {
      if (!isResizing) return;
      
      const delta = e.clientX - startX;
      const newWidth = Math.max(100, startWidth + delta);
      
      this.explorerContainer.style.width = `${newWidth}px`;
    });
    
    document.addEventListener('mouseup', () => {
      if (isResizing) {
        isResizing = false;
        document.body.style.userSelect = '';
      }
    });
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // File explorer events
    this.fileExplorer.on('folder-opened', (folderPath) => {
      console.log(`Folder opened: ${folderPath}`);
      this.emit('folder-opened', folderPath);
    });
    
    this.fileExplorer.on('file-selected', ({ path, content }) => {
      console.log(`File selected: ${path}`);
      this.currentFile = path;
      this.aceEditor.openFile(path, content);
      this.emit('file-selected', { path, content });
    });
  }

  /**
   * Handle editor content change
   * 
   * @param {string} content New content
   */
  handleEditorChange(content) {
    // Auto-save changes
    this.saveCurrentFile();
  }

  /**
   * Save the current file
   */
  async saveCurrentFile() {
    if (!this.currentFile || !window.api || !window.api.writeFile) return;
    
    try {
      const content = this.aceEditor.getContent();
      await window.api.writeFile(this.currentFile, content);
      
      // Emit event
      this.emit('file-saved', this.currentFile);
    } catch (error) {
      console.error('Error saving file:', error);
    }
  }

  /**
   * Open a folder
   * 
   * @param {string} folderPath Path to the folder
   */
  openFolder(folderPath) {
    if (!this.isInitialized) return;
    
    this.fileExplorer.currentPath = folderPath;
    this.fileExplorer.loadFileTree();
  }

  /**
   * Get the current file context
   * 
   * @returns {Object} File context object
   */
  getFileContext() {
    if (!this.currentFile) return null;
    
    return {
      path: this.currentFile,
      content: this.aceEditor.getContent(),
      language: path.extname(this.currentFile).substring(1)
    };
  }

  /**
   * Clean up resources
   */
  cleanup() {
    this.aceEditor.cleanup();
    this.isInitialized = false;
  }
}

module.exports = CodeEditor;