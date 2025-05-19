
/**
 * Chat Controller for CodeLve
 * 
 * Manages the chat UI and communication with the AI service
 */

class ChatController {
  constructor(codeContextProvider) {
    this.panel = null;
    this.messagesContainer = null;
    this.textarea = null;
    this.sendButton = null;
    this.codeContextProvider = codeContextProvider;
    this.isInitialized = false;
  }

  /**
   * Initialize the chat panel
   * 
   * @param {Element} container Container element
   * @returns {void}
   */
  initialize(container) {
    if (this.isInitialized) return;

    // Create panel elements
    this.panel = document.createElement("div");
    this.panel.className = "chat-panel";

    // Create messages container
    this.messagesContainer = document.createElement("div");
    this.messagesContainer.className = "messages-container";
    this.panel.appendChild(this.messagesContainer);

    // Create input area
    const inputContainer = document.createElement("div");
    inputContainer.className = "input-container";

    this.textarea = document.createElement("textarea");
    this.textarea.className = "chat-input";
    this.textarea.placeholder = "Ask about your code...";
    this.textarea.rows = 3;

    this.sendButton = document.createElement("button");
    this.sendButton.className = "send-button";
    this.sendButton.textContent = "Send";

    // Add event listeners
    this.sendButton.addEventListener("click", () => {
      this.sendMessage(this.textarea.value);
    });

    this.textarea.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage(this.textarea.value);
      }
    });

    // Append elements
    inputContainer.appendChild(this.textarea);
    inputContainer.appendChild(this.sendButton);
    this.panel.appendChild(inputContainer);

    // Append panel to container
    container.appendChild(this.panel);

    // Add welcome message
    this.addSystemMessage(
      "Welcome to CodeLve! Ask me anything about your code or how to implement new features."
    );

    this.isInitialized = true;
  }

  /**
   * Send a message to the AI
   * 
   * @param {string} content Message content
   */
  async sendMessage(content) {
    if (!content || !content.trim()) return;

    // Add user message
    this.addUserMessage(content);

    // Clear input
    this.textarea.value = "";

    // Add loading message
    const loadingId = this.addLoadingMessage();

    // Send to AI if API available
    if (window.api && window.api.queryAI) {
      try {
        // Get code context if available
        let codeContext = '';
        if (this.codeContextProvider) {
          codeContext = this.codeContextProvider.getContext();
          console.log('Including code context in AI query:', 
            codeContext ? `${codeContext.length} characters` : 'none');
        }
        
        const response = await window.api.queryAI({ 
          prompt: content, 
          context: codeContext 
        });
        
        // Remove loading message
        this.removeMessage(loadingId);
        
        if (response.error) {
          this.addSystemMessage(`Error: ${response.error}`);
        } else if (response.response) {
          // Clean up the response text to remove any remaining prompt text
          let cleanResponse = response.response;
          
          // Clean up common patterns that might be in the response
          cleanResponse = cleanResponse.replace(/^(CODELVE RESPONSE:|RESPONSE:)/i, '').trim();
          
          // Remove any trailing "[end of text]" markers
          cleanResponse = cleanResponse.replace(/\[end of text\]$/i, '').trim();
          
          // Add properly cleaned response to chat
          this.addAIMessage(cleanResponse);
        } else {
          this.addSystemMessage('Received empty response from AI.');
        }
      } catch (error) {
        // Remove loading message
        this.removeMessage(loadingId);
        this.addSystemMessage(`Error: Failed to get AI response. ${error.message || ''}`);
        console.error('Error querying AI:', error);
      }
    } else {
      // Remove loading message
      this.removeMessage(loadingId);
      this.addSystemMessage(
        "AI service not available. Please check if the AI server is installed and running."
      );
    }
  }

  /**
   * Add a user message to the chat
   * 
   * @param {string} content Message content
   */
  addUserMessage(content) {
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
      <div class="message-content">${this.escapeHTML(content)}</div>
    `;

    this.messagesContainer.appendChild(messageEl);
    this.scrollToBottom();
  }

  /**
   * Add an AI message to the chat
   * 
   * @param {string} content Message content
   */
  addAIMessage(content) {
    const messageEl = document.createElement("div");
    messageEl.className = "message ai-message";

    const time = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    // Process code blocks
    const processedContent = this.processCodeBlocks(content);

    messageEl.innerHTML = `
      <div class="message-header">
        <span class="message-sender">CodeLve</span>
        <span class="message-time">${time}</span>
      </div>
      <div class="message-content">${processedContent}</div>
    `;

    this.messagesContainer.appendChild(messageEl);
    this.scrollToBottom();
  }

  /**
   * Add a system message to the chat
   * 
   * @param {string} content Message content
   */
  addSystemMessage(content) {
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
      <div class="message-content">${this.escapeHTML(content)}</div>
    `;

    this.messagesContainer.appendChild(messageEl);
    this.scrollToBottom();
  }

  /**
   * Add a loading message to the chat
   * 
   * @returns {string} Message ID
   */
  addLoadingMessage() {
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

    this.messagesContainer.appendChild(loadingEl);
    this.scrollToBottom();

    return id;
  }

  /**
   * Remove a message from the chat
   * 
   * @param {string} id Message ID
   */
  removeMessage(id) {
    const messageEl = document.getElementById(id);
    if (messageEl) {
      messageEl.remove();
    }
  }

  /**
   * Process code blocks in message content with better syntax highlighting
   * 
   * @param {string} content Message content
   * @returns {string} Processed content
   */
  processCodeBlocks(content) {
    // Replace code blocks with styled elements
    let processedContent = content.replace(
      /```([\w]*)\n([\s\S]*?)```/g,
      (match, language, code) => {
        const langClass = language ? ` language-${language}` : "";
        const langLabel = language ? 
                          `<div class="code-block-language">${language}</div>` : 
                          "";
        
        // Replace tabs with spaces for better display
        const processedCode = code
          .replace(/\t/g, '  ')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;');
        
        return `
          <div class="code-block-container">
            ${langLabel}
            <pre class="code-block${langClass}"><code>${processedCode}</code></pre>
            <button class="copy-code-button" onclick="navigator.clipboard.writeText(\`${
              code.replace(/`/g, '\\`').replace(/\$/g, '\\$')
            }\`)">Copy</button>
          </div>
        `;
      }
    );
    
    // Also handle inline code
    processedContent = processedContent.replace(
      /`([^`]+)`/g,
      '<code class="inline-code">$1</code>'
    );
    
    return processedContent;
  }

  /**
   * Escape HTML in text
   * 
   * @param {string} html HTML string
   * @returns {string} Escaped HTML
   */
  escapeHTML(html) {
    const div = document.createElement("div");
    div.textContent = html;
    return div.innerHTML;
  }

  /**
   * Scroll to the bottom of the container
   */
  scrollToBottom() {
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  /**
   * Clear all messages
   */
  clearMessages() {
    this.messagesContainer.innerHTML = '';
    this.addSystemMessage('Chat cleared. Ask me anything about your code!');
  }
}

module.exports = ChatController;