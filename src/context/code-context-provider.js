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
    this.activeFile = filePath;
    this.updateFileContent(filePath, content);
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
    if (activeFileOnly) {
      const activeFile = this.getActiveFile();
      if (!activeFile) return '';
      
      return this.formatFileContext(activeFile.path, activeFile.content);
    }
    
    // Start with the active file
    let context = '';
    const activeFile = this.getActiveFile();
    
    if (activeFile) {
      context += this.formatFileContext(activeFile.path, activeFile.content);
    }
    
    // Add related files if space allows
    let remainingChars = this.maxContextSize - context.length;
    
    if (remainingChars > 0) {
      for (const [filePath, content] of this.openFiles.entries()) {
        // Skip the active file as we've already added it
        if (filePath === this.activeFile) continue;
        
        const fileContext = this.formatFileContext(filePath, content);
        
        // Check if we can fit this file in the context
        if (fileContext.length < remainingChars) {
          context += '\n\n' + fileContext;
          remainingChars -= fileContext.length + 2; // +2 for the newlines
        } else {
          // We can't fit the whole file, so just add a truncated version
          const truncatedContext = this.formatFileContext(
            filePath, 
            content.substring(0, remainingChars - 100) + '\n... (truncated)'
          );
          
          context += '\n\n' + truncatedContext;
          break;
        }
      }
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