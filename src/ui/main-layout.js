/**
 * Main Layout for CodeLve
 * 
 * Provides the split interface with code editor and chat panel
 */

class MainLayout {
    constructor() {
      this.container = null;
      this.editorContainer = null;
      this.chatContainer = null;
      this.resizeHandle = null;
      this.isInitialized = false;
      this.minWidth = 300; // Minimum width for panels
      this.splitRatio = 0.6; // Default split: 60% editor, 40% chat
    }
  
    /**
     * Initialize the layout
     * 
     * @param {Element} container The container element
     * @returns {Object} Container elements for editor and chat
     */
    initialize(container) {
      if (this.isInitialized) {
        return {
          editorContainer: this.editorContainer,
          chatContainer: this.chatContainer
        };
      }
  
      console.log('Initializing main layout');
      
      this.container = container;
      this.container.classList.add('main-layout');
      
      // Create split containers
      this.editorContainer = document.createElement('div');
      this.editorContainer.className = 'editor-container';
      
      this.chatContainer = document.createElement('div');
      this.chatContainer.className = 'chat-container';
      
      // Create resize handle
      this.resizeHandle = document.createElement('div');
      this.resizeHandle.className = 'resize-handle';
      
      // Append elements
      this.container.appendChild(this.editorContainer);
      this.container.appendChild(this.resizeHandle);
      this.container.appendChild(this.chatContainer);
      
      // Set initial sizes
      this.updateSplit();
      
      // Add event listeners for resize
      this.setupResizeHandling();
      
      // Handle window resize
      window.addEventListener('resize', () => this.updateSplit());
      
      this.isInitialized = true;
      
      return {
        editorContainer: this.editorContainer,
        chatContainer: this.chatContainer
      };
    }
  
    /**
     * Set up resize handling for the split interface
     */
    setupResizeHandling() {
      let isDragging = false;
      let startX = 0;
      let startWidth = 0;
      
      this.resizeHandle.addEventListener('mousedown', (e) => {
        isDragging = true;
        startX = e.clientX;
        startWidth = this.editorContainer.offsetWidth;
        this.resizeHandle.classList.add('dragging');
        
        // Prevent text selection during drag
        document.body.style.userSelect = 'none';
      });
      
      document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        
        const containerWidth = this.container.offsetWidth;
        const deltaX = e.clientX - startX;
        const newWidth = Math.min(
          Math.max(startWidth + deltaX, this.minWidth),
          containerWidth - this.minWidth
        );
        
        this.splitRatio = newWidth / containerWidth;
        this.updateSplit();
      });
      
      document.addEventListener('mouseup', () => {
        if (isDragging) {
          isDragging = false;
          this.resizeHandle.classList.remove('dragging');
          document.body.style.userSelect = '';
        }
      });
    }
  
    /**
     * Update the split layout based on current ratio
     */
    updateSplit() {
      if (!this.isInitialized) return;
      
      const containerWidth = this.container.offsetWidth;
      const editorWidth = Math.round(containerWidth * this.splitRatio);
      const chatWidth = containerWidth - editorWidth;
      
      this.editorContainer.style.width = `${editorWidth}px`;
      this.chatContainer.style.width = `${chatWidth}px`;
    }
  
    /**
     * Set the split ratio
     * 
     * @param {number} ratio Ratio between 0 and 1
     */
    setSplitRatio(ratio) {
      if (ratio < 0 || ratio > 1) return;
      
      this.splitRatio = ratio;
      this.updateSplit();
    }
  }
  
  module.exports = MainLayout;