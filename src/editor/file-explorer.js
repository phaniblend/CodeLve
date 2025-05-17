/**
 * File Explorer Component for CodeLve
 */

const EventEmitter = require('events');
const path = require('path');
const fs = require('fs');

class FileExplorer extends EventEmitter {
  constructor() {
    super();
    this.container = null;
    this.isInitialized = false;
    this.currentPath = null;
    this.fileTree = null;
    this.selectedFile = null;
  }

  /**
   * Initialize the File Explorer
   * 
   * @param {Element} container The container element
   * @returns {void}
   */
  initialize(container) {
    if (this.isInitialized) return;

    this.container = container;
    this.container.className = 'file-explorer';
    
    // Create the explorer UI
    this.createExplorerUI();
    
    this.isInitialized = true;
  }

  /**
   * Create the explorer UI
   */
  createExplorerUI() {
    // Clear container
    this.container.innerHTML = '';
    
    // Create header
    const header = document.createElement('div');
    header.className = 'explorer-header';
    
    const title = document.createElement('div');
    title.className = 'explorer-title';
    title.textContent = 'Explorer';
    
    const actions = document.createElement('div');
    actions.className = 'explorer-actions';
    
    const openButton = document.createElement('button');
    openButton.className = 'explorer-action';
    openButton.title = 'Open Folder';
    openButton.innerHTML = '📂';
    openButton.addEventListener('click', () => this.openFolder());
    
    const refreshButton = document.createElement('button');
    refreshButton.className = 'explorer-action';
    refreshButton.title = 'Refresh';
    refreshButton.innerHTML = '🔄';
    refreshButton.addEventListener('click', () => this.refresh());
    
    const newFileButton = document.createElement('button');
    newFileButton.className = 'explorer-action';
    newFileButton.title = 'New File';
    newFileButton.innerHTML = '📄';
    newFileButton.addEventListener('click', () => this.createNewFile());
    
    actions.appendChild(openButton);
    actions.appendChild(refreshButton);
    actions.appendChild(newFileButton);
    
    header.appendChild(title);
    header.appendChild(actions);
    
    // Create content container
    const content = document.createElement('div');
    content.className = 'explorer-content';
    
    // Add placeholder message
    if (!this.currentPath) {
      const placeholder = document.createElement('div');
      placeholder.className = 'explorer-placeholder';
      placeholder.textContent = 'No folder opened yet. Click the folder icon to open a project.';
      content.appendChild(placeholder);
    }
    
    // Add to container
    this.container.appendChild(header);
    this.container.appendChild(content);
    
    // Fill with file tree if we have a current path
    if (this.currentPath) {
      this.loadFileTree();
    }
  }

  /**
   * Open a folder as the root of the file explorer
   */
  async openFolder() {
    if (!window.api || !window.api.showOpenDialog) return;
    
    try {
      const result = await window.api.showOpenDialog({
        properties: ['openDirectory']
      });
      
      if (!result.canceled && result.filePaths && result.filePaths.length > 0) {
        this.currentPath = result.filePaths[0];
        this.loadFileTree();
        this.emit('folder-opened', this.currentPath);
      }
    } catch (error) {
      console.error('Error opening folder:', error);
    }
  }

  /**
   * Load the file tree for the current path
   */
  async loadFileTree() {
    if (!this.currentPath || !window.api || !window.api.listDirectory) return;
    
    try {
      const items = await window.api.listDirectory(this.currentPath);
      this.fileTree = this.buildFileTree(items);
      this.renderFileTree();
    } catch (error) {
      console.error('Error loading file tree:', error);
    }
  }

  /**
   * Build a file tree from directory items
   * 
   * @param {Array} items Directory items
   * @returns {Object} File tree object
   */
  buildFileTree(items) {
    // Sort: directories first, then files, both alphabetically
    items.sort((a, b) => {
      if (a.isDirectory && !b.isDirectory) return -1;
      if (!a.isDirectory && b.isDirectory) return 1;
      return a.name.localeCompare(b.name);
    });
    
    return {
      name: path.basename(this.currentPath),
      path: this.currentPath,
      isDirectory: true,
      children: items
    };
  }

  /**
   * Render the file tree
   */
  renderFileTree() {
    if (!this.fileTree) return;
    
    const content = this.container.querySelector('.explorer-content');
    if (!content) return;
    
    // Clear content
    content.innerHTML = '';
    
    // Create tree view
    const treeView = document.createElement('div');
    treeView.className = 'tree-view';
    
    // Add root node
    const rootNode = this.createTreeNode(this.fileTree, 0);
    treeView.appendChild(rootNode);
    
    // Add to content
    content.appendChild(treeView);
  }

  /**
   * Create a tree node element
   * 
   * @param {Object} item File tree item
   * @param {number} level Nesting level
   * @returns {Element} Tree node element
   */
  createTreeNode(item, level) {
    const node = document.createElement('div');
    node.className = 'tree-node';
    node.style.paddingLeft = `${level * 16}px`;
    
    const nodeContent = document.createElement('div');
    nodeContent.className = 'node-content';
    
    const icon = document.createElement('span');
    icon.className = 'node-icon';
    icon.textContent = item.isDirectory ? '📁' : '📄';
    
    const name = document.createElement('span');
    name.className = 'node-name';
    name.textContent = item.name;
    
    nodeContent.appendChild(icon);
    nodeContent.appendChild(name);
    node.appendChild(nodeContent);
    
    // Make node clickable
    nodeContent.addEventListener('click', (e) => {
      if (item.isDirectory) {
        // Toggle directory expansion
        const childrenContainer = node.querySelector('.node-children');
        if (childrenContainer) {
          childrenContainer.style.display = 
            childrenContainer.style.display === 'none' ? 'block' : 'none';
          icon.textContent = childrenContainer.style.display === 'none' ? '📁' : '📂';
        } else {
          // Load directory contents
          this.expandDirectory(node, item, level);
        }
      } else {
        // Select and open file
        this.selectFile(item.path);
      }
    });
    
    return node;
  }

  /**
   * Expand a directory in the tree view
   * 
   * @param {Element} parentNode Parent node element
   * @param {Object} item Directory item
   * @param {number} level Nesting level
   */
  async expandDirectory(parentNode, item, level) {
    if (!window.api || !window.api.listDirectory) return;
    
    try {
      // Get directory contents
      const items = await window.api.listDirectory(item.path);
      
      // Create children container
      const childrenContainer = document.createElement('div');
      childrenContainer.className = 'node-children';
      
      // Sort: directories first, then files, both alphabetically
      items.sort((a, b) => {
        if (a.isDirectory && !b.isDirectory) return -1;
        if (!a.isDirectory && b.isDirectory) return 1;
        return a.name.localeCompare(b.name);
      });
      
      // Add child nodes
      for (const child of items) {
        const childNode = this.createTreeNode(child, level + 1);
        childrenContainer.appendChild(childNode);
      }
      
      // Add children container to parent node
      parentNode.appendChild(childrenContainer);
      
      // Update icon
      const icon = parentNode.querySelector('.node-icon');
      if (icon) {
        icon.textContent = '📂';
      }
    } catch (error) {
      console.error('Error expanding directory:', error);
    }
  }

  /**
   * Select and open a file
   * 
   * @param {string} filePath Path to the file
   */
  async selectFile(filePath) {
    if (!window.api || !window.api.readFile) return;
    
    try {
      // Read file content
      const content = await window.api.readFile(filePath);
      
      // Select file
      this.selectedFile = filePath;
      
      // Emit event
      this.emit('file-selected', {
        path: filePath,
        content
      });
    } catch (error) {
      console.error('Error selecting file:', error);
    }
  }

  /**
   * Refresh the file tree
   */
  refresh() {
    if (!this.currentPath) return;
    
    this.loadFileTree();
  }

  /**
   * Create a new file
   */
  async createNewFile() {
    if (!this.currentPath || !window.api) return;
    
    const fileName = prompt('Enter file name:');
    if (!fileName) return;
    
    try {
      const filePath = path.join(this.currentPath, fileName);
      
      // Use the window.api to check if file exists and create it
      try {
        await window.api.readFile(filePath);
        // If we get here, the file exists
        alert(`File "${fileName}" already exists.`);
        return;
      } catch (e) {
        // File doesn't exist, continue to create it
      }
      
      // Create empty file
      await window.api.writeFile(filePath, '');
      
      // Refresh file tree
      this.refresh();
      
      // Open the new file
      this.selectFile(filePath);
    } catch (error) {
      console.error('Error creating file:', error);
    }
  }
}

module.exports = FileExplorer;