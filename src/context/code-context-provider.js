/**
 * Code Context Provider for CodeLve
 * 
 * Manages extraction and provision of code context from the active files 
 * to the AI assistant
 */

const path = require('path');
const fs = require('fs');

class CodeContextProvider {
  constructor() {
    this.activeFile = null;
    this.openFiles = new Map(); // Map of file paths to their content
    this.activeProject = null;
    this.fileWatchers = new Map(); // Map of file paths to their watchers
    this.maxContextSize = 10000; // Maximum number of characters to send as context
  }

  /**
   * Set the active file being edited
   * 
   * @param {string} filePath Path to the active file
   * @param {string} content Current content of the file
   */
  setActiveFile(filePath, content) {
    if (!filePath) return;
    
    this.activeFile = filePath;
    this.openFiles.set(filePath, content);
    
    console.log(`Active file set to: ${filePath}`);
    
    // Start watching this file for changes if not already watching
    this.watchFile(filePath);
  }

  /**
   * Update the content of a file in the context
   * 
   * @param {string} filePath Path to the file
   * @param {string} content Current content of the file
   */
  updateFileContent(filePath, content) {
    if (!filePath) return;
    
    this.openFiles.set(filePath, content);
    
    // Start watching this file for changes if not already watching
    this.watchFile(filePath);
  }

  /**
   * Set the active project/workspace
   * 
   * @param {string} projectPath Path to the project root
   */
  setActiveProject(projectPath) {
    this.activeProject = projectPath;
    // Could scan project structure here or on-demand
  }

  /**
   * Watch a file for changes
   * 
   * @param {string} filePath Path to the file to watch
   */
  watchFile(filePath) {
    if (this.fileWatchers.has(filePath)) return;
    
    try {
      const watcher = fs.watch(filePath, (eventType) => {
        if (eventType === 'change') {
          // File was changed externally, reload content
          this.reloadFileContent(filePath);
        }
      });
      
      this.fileWatchers.set(filePath, watcher);
    } catch (error) {
      console.error(`Error watching file ${filePath}:`, error);
    }
  }

  /**
   * Reload file content from disk
   * 
   * @param {string} filePath Path to the file
   */
  reloadFileContent(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      this.openFiles.set(filePath, content);
    } catch (error) {
      console.error(`Error reloading file ${filePath}:`, error);
    }
  }

  /**
   * Stop watching a file
   * 
   * @param {string} filePath Path to the file
   */
  unwatchFile(filePath) {
    const watcher = this.fileWatchers.get(filePath);
    
    if (watcher) {
      watcher.close();
      this.fileWatchers.delete(filePath);
    }
  }

  /**
   * Remove a file from the context
   * 
   * @param {string} filePath Path to the file
   */
  removeFile(filePath) {
    this.openFiles.delete(filePath);
    this.unwatchFile(filePath);
    
    // If this was the active file, set active file to null
    if (this.activeFile === filePath) {
      this.activeFile = null;
    }
  }

  /**
   * Get the active file path and content
   * 
   * @returns {Object|null} Object with path and content, or null if no active file
   */
  getActiveFile() {
    if (!this.activeFile) return null;
    
    return {
      path: this.activeFile,
      content: this.openFiles.get(this.activeFile)
    };
  }

  /**
   * Get context for the AI based on the current state
   * 
   * @param {boolean} activeFileOnly If true, only include the active file
   * @returns {string} Context string for the AI
   */
  getContext(activeFileOnly = false) {
    // If we have an active file, use it
    if (this.activeFile && this.openFiles.has(this.activeFile)) {
      const content = this.openFiles.get(this.activeFile);
      return this.formatFileContext(this.activeFile, content);
    }
    
    // If the global code editor is available, try to get context from it
    if (window.codeEditor && typeof window.codeEditor.getFileContext === 'function') {
      const fileContext = window.codeEditor.getFileContext();
      if (fileContext && fileContext.path && fileContext.content) {
        return this.formatFileContext(fileContext.path, fileContext.content);
      }
    }

    // If activeFileOnly is true, return empty string if no active file
    if (activeFileOnly) return '';
    
    // Otherwise, include other open files
    let context = '';
    
    // Calculate remaining context size
    let remainingSize = this.maxContextSize;
    
    // Add open files to context until max size is reached
    for (const [filePath, content] of this.openFiles.entries()) {
      // Skip if this would exceed max context size
      const fileContext = this.formatFileContext(filePath, content);
      if (fileContext.length > remainingSize) continue;
      
      // Add file context with separator
      if (context) context += '\n\n';
      context += fileContext;
      
      // Update remaining size
      remainingSize -= fileContext.length;
      
      // Break if no more room
      if (remainingSize <= 0) break;
    }
    
    // If no context was added, return default example
    if (!context) {
      return 'File: test.js\nPath: /test.js\nType: js\n\n```js\n// Sample code for testing\nfunction hello() {\n  console.log("Hello, world!");\n}\n```';
    }
    
    return context;
  }

  /**
   * Format a file's content as context for the AI
   * 
   * @param {string} filePath Path to the file
   * @param {string} content Content of the file
   * @returns {string} Formatted context
   */
  formatFileContext(filePath, content) {
    const fileName = path.basename(filePath);
    const fileExt = path.extname(filePath).substring(1); // Remove the dot
    
    return `File: ${fileName}\nPath: ${filePath}\nType: ${fileExt}\n\n\`\`\`${fileExt}\n${content}\n\`\`\``;
  }

  /**
   * Clean up resources
   */
  cleanup() {
    // Stop all file watchers
    for (const [filePath, watcher] of this.fileWatchers.entries()) {
      watcher.close();
    }
    
    this.fileWatchers.clear();
    this.openFiles.clear();
    this.activeFile = null;
    this.activeProject = null;
  }
}

module.exports = CodeContextProvider;