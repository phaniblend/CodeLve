/**
 * Chat Panel for CodeLve
 * 
 * Provides the UI for interacting with the AI assistant
 */

const EventEmitter = require('events');

class ChatPanel extends EventEmitter {
  constructor() {
    super();
    this.messages = [];
    this.isInitialized = false;
    this.panel = null;
    this.inputElement = null;
    this.messagesElement = null;
  }

  /**
   * Initialize the chat panel
   * 
   * @param {Element} container The container element
   * @returns {void}
   */
  initialize(container) {
    if (this.isInitialized) return;

    console.log('Initializing chat panel');
    
    // Create panel elements
    this.panel = document.createElement('div');
    this.panel.className = 'chat-panel';
    
    // Create messages container
    this.messagesElement = document.createElement('div');
    this.messagesElement.className = 'messages-container';
    this.panel.appendChild(this.messagesElement);
    
    // Create input area
    const inputContainer = document.createElement('div');
    inputContainer.className = 'input-container';
    
    this.inputElement = document.createElement('textarea');
    this.inputElement.className = 'chat-input';
    this.inputElement.placeholder = 'Ask about your code...';
    this.inputElement.rows = 3;
    
    const sendButton = document.createElement('button');
    sendButton.className = 'send-button';
    sendButton.textContent = 'Send';
    
    // Add event listeners
    sendButton.addEventListener('click', () => this.sendMessage());
    
    this.inputElement.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    
    // Append elements
    inputContainer.appendChild(this.inputElement);
    inputContainer.appendChild(sendButton);
    this.panel.appendChild(inputContainer);
    
    // Append panel to container
    container.appendChild(this.panel);
    
    // Add system welcome message
    this.addSystemMessage('Welcome to CodeLve! Ask me anything about your code or how to implement new features.');
    
    this.isInitialized = true;
  }

  /**
   * Send a message to the AI
   */
  sendMessage() {
    const content = this.inputElement.value.trim();
    if (!content) return;
    
    // Add user message to chat
    this.addUserMessage(content);
    
    // Clear input
    this.inputElement.value = '';
    
    // Emit event for message sent
    this.emit('message', content);
    
    // Show loading indicator
    this.addLoadingMessage();
  }

  /**
   * Add a user message to the chat
   * 
   * @param {string} content Message content
   */
  addUserMessage(content) {
    const message = {
      id: Date.now(),
      type: 'user',
      content,
      timestamp: new Date()
    };
    
    this.messages.push(message);
    this.renderMessage(message);
  }

  /**
   * Add an AI response message to the chat
   * 
   * @param {string} content Message content
   */
  addAIMessage(content) {
    // Remove loading message if present
    this.removeLoadingMessage();
    
    const message = {
      id: Date.now(),
      type: 'ai',
      content,
      timestamp: new Date()
    };
    
    this.messages.push(message);
    this.renderMessage(message);
  }

  /**
   * Add a system message to the chat
   * 
   * @param {string} content Message content
   */
  addSystemMessage(content) {
    const message = {
      id: Date.now(),
      type: 'system',
      content,
      timestamp: new Date()
    };
    
    this.messages.push(message);
    this.renderMessage(message);
  }

  /**
   * Add a loading message to indicate AI is thinking
   */
  addLoadingMessage() {
    const loadingEl = document.createElement('div');
    loadingEl.className = 'message loading-message';
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
    
    loadingEl.id = 'loading-message';
    this.messagesElement.appendChild(loadingEl);
    this.scrollToBottom();
  }

  /**
   * Remove the loading message
   */
  removeLoadingMessage() {
    const loadingEl = document.getElementById('loading-message');
    if (loadingEl) {
      loadingEl.remove();
    }
  }

  /**
   * Render a message in the chat
   * 
   * @param {Object} message Message object
   */
  renderMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${message.type}-message`;
    
    // Format timestamp
    const time = message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Create message content with appropriate styling
    let content = message.content;
    
    // Process markdown-like code blocks
    content = this.processCodeBlocks(content);
    
    // Create message HTML
    messageEl.innerHTML = `
      <div class="message-header">
        <span class="message-sender">${this.getSenderName(message.type)}</span>
        <span class="message-time">${time}</span>
      </div>
      <div class="message-content">${content}</div>
    `;
    
    // Add to messages container
    this.messagesElement.appendChild(messageEl);
    
    // Scroll to bottom
    this.scrollToBottom();
  }

  /**
   * Process code blocks in message content
   * 
   * @param {string} content Message content
   * @returns {string} Processed content
   */
  processCodeBlocks(content) {
    // Replace code blocks with styled elements
    return content.replace(/```([\w]*)\n([\s\S]*?)```/g, (match, language, code) => {
      const langClass = language ? ` language-${language}` : '';
      return `<pre class="code-block${langClass}"><code>${this.escapeHTML(code)}</code></pre>`;
    });
  }

  /**
   * Get sender name based on message type
   * 
   * @param {string} type Message type
   * @returns {string} Sender name
   */
  getSenderName(type) {
    switch (type) {
      case 'user': return 'You';
      case 'ai': return 'CodeLve';
      case 'system': return 'System';
      default: return 'Unknown';
    }
  }

  /**
   * Escape HTML in text
   * 
   * @param {string} html HTML string
   * @returns {string} Escaped HTML
   */
  escapeHTML(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
  }

  /**
   * Scroll to the bottom of the chat
   */
  scrollToBottom() {
    this.messagesElement.scrollTop = this.messagesElement.scrollHeight;
  }

  /**
   * Handle AI response
   * 
   * @param {Object} response Response from AI
   */
  handleAIResponse(response) {
    if (response.error) {
      this.addSystemMessage(`Error: ${response.error}`);
      return;
    }
    
    this.addAIMessage(response.response);
  }

  /**
   * Clear all messages from the chat
   */
  clearMessages() {
    this.messages = [];
    this.messagesElement.innerHTML = '';
    
    // Add welcome message
    this.addSystemMessage('Chat cleared. Ask me anything about your code!');
  }
}

module.exports = ChatPanel;