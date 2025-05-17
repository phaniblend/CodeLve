/**
 * CodeLve Editor - Built on Ace Editor
 */

const path = require('path');

class AceEditor {
  constructor() {
    this.editor = null;
    this.container = null;
    this.isInitialized = false;
    this.currentFile = null;
    this.onChange = null;
  }

  /**
   * Initialize the Ace Editor
   * 
   * @param {Element} container The container element
   * @param {Function} onChange Callback when content changes
   * @returns {Object} The editor instance
   */
  initialize(container, onChange = null) {
    if (this.isInitialized) return this.editor;

    this.container = container;
    this.onChange = onChange;
    
    // Create editor container
    const editorContainer = document.createElement('div');
    editorContainer.className = 'ace-editor';
    editorContainer.style.width = '100%';
    editorContainer.style.height = '100%';
    
    // Add to container
    this.container.appendChild(editorContainer);
    
    // Try to load Ace using require
    try {
      const ace = require('ace-builds');
      require('ace-builds/src-noconflict/mode-javascript');
      require('ace-builds/src-noconflict/theme-monokai');
      
      // Create editor
      this.editor = ace.edit(editorContainer);
      this.editor.setTheme('ace/theme/monokai');
      this.editor.session.setMode('ace/mode/javascript');
      this.editor.setOptions({
        fontSize: '14px',
        showPrintMargin: false,
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: true
      });
      
      // Setup change event listener
      if (this.onChange) {
        this.editor.session.on('change', () => {
          this.onChange(this.editor.getValue());
        });
      }
    } catch (err) {
      console.error('Failed to load Ace editor:', err);
      
      // Fallback to a simple textarea if Ace cannot be loaded
      editorContainer.innerHTML = '';
      const textarea = document.createElement('textarea');
      textarea.style.width = '100%';
      textarea.style.height = '100%';
      textarea.style.fontFamily = 'monospace';
      textarea.style.fontSize = '14px';
      textarea.style.padding = '10px';
      textarea.style.resize = 'none';
      textarea.style.border = 'none';
      textarea.style.outline = 'none';
      
      editorContainer.appendChild(textarea);
      
      // Simple editor API to match Ace interface
      this.editor = {
        getValue: () => textarea.value,
        setValue: (value) => { textarea.value = value; },
        session: {
          setMode: () => {} // No-op for textarea
        },
        setTheme: () => {} // No-op for textarea
      };
      
      // Add change event listener to textarea
      if (this.onChange) {
        textarea.addEventListener('input', () => {
          this.onChange(textarea.value);
        });
      }
    }
    
    this.isInitialized = true;
    return this.editor;
  }

  /**
   * Set editor content
   * 
   * @param {string} content Content to set
   */
  setContent(content) {
    if (!this.isInitialized || !this.editor) return;
    
    this.editor.setValue(content || '', -1); // -1 to put cursor at the start
  }

  /**
   * Get editor content
   * 
   * @returns {string} Editor content
   */
  getContent() {
    if (!this.isInitialized || !this.editor) return '';
    
    return this.editor.getValue();
  }

  /**
   * Set the language mode
   * 
   * @param {string} filePath Path to the file (to determine language)
   */
  setLanguageMode(filePath) {
    if (!this.isInitialized || !this.editor) return;
    
    const ext = path.extname(filePath).toLowerCase();
    let mode = 'ace/mode/text'; // Default mode
    
    // Map file extensions to Ace modes
    const modeMap = {
      '.js': 'ace/mode/javascript',
      '.jsx': 'ace/mode/jsx',
      '.ts': 'ace/mode/typescript',
      '.tsx': 'ace/mode/tsx',
      '.html': 'ace/mode/html',
      '.css': 'ace/mode/css',
      '.json': 'ace/mode/json',
      '.py': 'ace/mode/python',
      '.java': 'ace/mode/java',
      '.c': 'ace/mode/c_cpp',
      '.cpp': 'ace/mode/c_cpp',
      '.h': 'ace/mode/c_cpp',
      '.cs': 'ace/mode/csharp',
      '.php': 'ace/mode/php',
      '.rb': 'ace/mode/ruby',
      '.md': 'ace/mode/markdown',
      '.xml': 'ace/mode/xml',
      '.sql': 'ace/mode/sql',
      '.sh': 'ace/mode/sh',
      '.bat': 'ace/mode/batchfile',
      '.yaml': 'ace/mode/yaml',
      '.yml': 'ace/mode/yaml'
    };
    
    if (modeMap[ext]) {
      mode = modeMap[ext];
      
      try {
        // Try to load the mode
        require(`ace-builds/src-noconflict/mode-${mode.split('/').pop()}`);
        this.editor.session.setMode(mode);
      } catch (err) {
        console.warn(`Mode ${mode} not available, using text mode`);
        this.editor.session.setMode('ace/mode/text');
      }
    } else {
      this.editor.session.setMode(mode);
    }
  }

  /**
   * Open a file
   * 
   * @param {string} filePath Path to the file
   * @param {string} content File content
   */
  openFile(filePath, content) {
    if (!this.isInitialized || !this.editor) return;
    
    this.currentFile = filePath;
    
    // Set language mode based on file extension
    this.setLanguageMode(filePath);
    
    // Set content
    this.setContent(content);
  }

  /**
   * Set editor theme
   * 
   * @param {string} theme Theme name
   */
  setTheme(theme) {
    if (!this.isInitialized || !this.editor) return;
    
    try {
      // Try to load the theme
      require(`ace-builds/src-noconflict/theme-${theme}`);
      this.editor.setTheme(`ace/theme/${theme}`);
    } catch (err) {
      console.warn(`Theme ${theme} not available`);
    }
  }

  /**
   * Clean up resources
   */
  cleanup() {
    if (this.editor && typeof this.editor.destroy === 'function') {
      this.editor.destroy();
      this.editor = null;
    }
    
    this.isInitialized = false;
  }
}

module.exports = AceEditor;