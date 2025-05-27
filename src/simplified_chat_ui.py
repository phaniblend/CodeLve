import os
import threading
import time
import webbrowser
from pathlib import Path
import markdown
import re

class SimplifiedChatUI:
    def __init__(self, ai_client, memory_manager):
        self.ai_client = ai_client
        self.memory_manager = memory_manager
        self.server = None
        self.port = 8501
        self.conversation = []
        self.is_processing = False
        
    def create_styles(self):
        """Create chat UI styles with theme toggle"""
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');
        
        * {
            box-sizing: border-box;
        }
        
        /* Dark Theme (Default) */
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            margin: 0;
            padding: 0;
            background: #23272E;
            color: #ECEDEE;
            height: 100vh;
            overflow: hidden;
            line-height: 1.6;
            transition: all 0.3s ease;
        }
        
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            max-width: 1200px;
            margin: 0 auto;
            background: #23272E;
            transition: all 0.3s ease;
        }
        
        .header {
            background: linear-gradient(135deg, #294060 0%, #273040 100%);
            padding: 20px 30px;
            border-bottom: 2px solid #49516B;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }
        
        .header-left h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 600;
            color: #ECEDEE;
        }
        
        .header-left .subtitle {
            margin: 4px 0 0 0;
            font-size: 14px;
            color: #8B949E;
            font-weight: 400;
        }
        
        .header-right {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        .theme-toggle {
            background: #49516B;
            border: none;
            color: #ECEDEE;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .theme-toggle:hover {
            background: #5A6478;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px 30px;
            overflow-y: auto;
            background: #23272E;
            scroll-behavior: smooth;
            transition: all 0.3s ease;
        }
        
        .chat-messages::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-messages::-webkit-scrollbar-track {
            background: #273040;
            border-radius: 4px;
        }
        
        .chat-messages::-webkit-scrollbar-thumb {
            background: #49516B;
            border-radius: 4px;
        }
        
        .message {
            margin-bottom: 24px;
            padding: 20px;
            border-radius: 12px;
            max-width: 85%;
            word-wrap: break-word;
            position: relative;
            transition: all 0.3s ease;
        }
        
        .user-message {
            background: linear-gradient(135deg, #82AAFF 0%, #7FDBCA 100%);
            color: #23272E;
            margin-left: auto;
            border: 1px solid #82AAFF;
            font-weight: 500;
        }
        
        .ai-message {
            background: #294060;
            color: #ECEDEE;
            border: 1px solid #49516B;
            margin-right: auto;
        }
        
        .message-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .copy-button {
            background: #49516B;
            border: none;
            color: #8B949E;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            opacity: 0;
            transition: all 0.2s ease;
        }
        
        .ai-message:hover .copy-button {
            opacity: 1;
        }
        
        .copy-button:hover {
            background: #5A6478;
            color: #ECEDEE;
        }
        
        .copy-button.copied {
            background: #A3BE8C;
            color: #23272E;
        }
        
        .ai-message code {
            background: #273040;
            color: #C792EA;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            border: 1px solid #49516B;
        }
        
        .ai-message pre {
            background: #1A1D23;
            color: #ECEDEE;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            line-height: 1.5;
            border: 1px solid #49516B;
            margin: 12px 0;
            position: relative;
        }
        
        .ai-message pre::before {
            content: 'Copy';
            position: absolute;
            top: 8px;
            right: 8px;
            background: #49516B;
            color: #8B949E;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s ease;
        }
        
        .ai-message pre:hover::before {
            opacity: 1;
        }
        
        .input-container {
            padding: 20px 30px;
            background: #273040;
            border-top: 2px solid #49516B;
            display: flex;
            gap: 12px;
            align-items: flex-end;
            transition: all 0.3s ease;
        }
        
        #chat-input {
            flex: 1;
            min-height: 44px;
            max-height: 120px;
            padding: 12px 16px;
            border: 2px solid #49516B;
            border-radius: 8px;
            background: #23272E;
            color: #ECEDEE;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            line-height: 1.5;
            resize: vertical;
            transition: all 0.2s ease;
        }
        
        #chat-input:focus {
            outline: none;
            border-color: #82AAFF;
        }
        
        #send-button {
            padding: 12px 20px;
            background: linear-gradient(135deg, #82AAFF 0%, #7FDBCA 100%);
            color: #23272E;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
            min-width: 80px;
            height: 44px;
        }
        
        #send-button:hover {
            transform: translateY(-1px);
        }
        
        #send-button:disabled {
            background: #49516B;
            color: #8B949E;
            cursor: not-allowed;
            transform: none;
        }
        
        /* Light Theme */
        body.light-theme {
            background: #FAFBFC;
            color: #30343F;
        }
        
        .light-theme .chat-container {
            background: #FAFBFC;
        }
        
        .light-theme .header {
            background: linear-gradient(135deg, #E9EDF2 0%, #F5F7FA 100%);
            border-bottom-color: #D1D5DB;
        }
        
        .light-theme .header-left h1 {
            color: #30343F;
        }
        
        .light-theme .header-left .subtitle {
            color: #A6ACB8;
        }
        
        .light-theme .theme-toggle {
            background: #D1D5DB;
            color: #30343F;
        }
        
        .light-theme .theme-toggle:hover {
            background: #A6ACB8;
        }
        
        .light-theme .chat-messages {
            background: #FAFBFC;
        }
        
        .light-theme .chat-messages::-webkit-scrollbar-track {
            background: #E9EDF2;
        }
        
        .light-theme .chat-messages::-webkit-scrollbar-thumb {
            background: #D1D5DB;
        }
        
        .light-theme .user-message {
            background: linear-gradient(135deg, #2466B1 0%, #158C86 100%);
            color: #FAFBFC;
            border-color: #2466B1;
        }
        
        .light-theme .ai-message {
            background: #E9EDF2;
            color: #30343F;
            border-color: #D1D5DB;
        }
        
        .light-theme .copy-button {
            background: #D1D5DB;
            color: #A6ACB8;
        }
        
        .light-theme .copy-button:hover {
            background: #A6ACB8;
            color: #30343F;
        }
        
        .light-theme .ai-message code {
            background: #F5F7FA;
            color: #7D4DAF;
            border-color: #D1D5DB;
        }
        
        .light-theme .ai-message pre {
            background: #F5F7FA;
            color: #30343F;
            border-color: #D1D5DB;
        }
        
        .light-theme .input-container {
            background: #E9EDF2;
            border-top-color: #D1D5DB;
        }
        
        .light-theme #chat-input {
            background: #FAFBFC;
            color: #30343F;
            border-color: #D1D5DB;
        }
        
        .light-theme #chat-input:focus {
            border-color: #2466B1;
        }
        
        .light-theme #send-button {
            background: linear-gradient(135deg, #2466B1 0%, #158C86 100%);
            color: #FAFBFC;
        }
        
        .light-theme #send-button:disabled {
            background: #D1D5DB;
            color: #A6ACB8;
        }
        
        @media (max-width: 768px) {
            .header {
                padding: 16px 20px;
                flex-direction: column;
                gap: 12px;
            }
            
            .header-right {
                align-self: flex-end;
            }
            
            .chat-messages {
                padding: 16px 20px;
            }
            
            .message {
                max-width: 95%;
                padding: 16px;
            }
            
            .input-container {
                padding: 16px 20px;
            }
        }
        </style>
        """

    def create_html(self):
        """Create the main HTML structure"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CodeLve - AI Code Assistant</title>
            {self.create_styles()}
            <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/4.3.0/marked.min.js"></script>
        </head>
        <body>
            <div class="chat-container">
                <div class="header">
                    <div class="header-left">
                        <h1>🚀 CodeLve</h1>
                        <div class="subtitle">AI-Powered Codebase Assistant</div>
                    </div>
                    <div class="header-right">
                        <button class="theme-toggle" onclick="toggleTheme()">🌙 Dark</button>
                    </div>
                </div>
                
                <div class="chat-messages" id="chat-messages">
                    <div class="ai-message">
                        <div class="message-header">
                            <strong>🤖 CodeLve Assistant</strong>
                            <button class="copy-button" onclick="copyMessage(this)">Copy</button>
                        </div>
                        <p>Hello! I'm your AI codebase assistant. I can help you:</p>
                        <ul>
                            <li><strong>Analyze components:</strong> "explain UserProfile component"</li>
                            <li><strong>Find functions:</strong> "show handleSubmit from FormUtils.js"</li>
                            <li><strong>Search codebase:</strong> "find api services"</li>
                            <li><strong>Analyze files:</strong> "analyze package.json"</li>
                        </ul>
                        <p>What would you like to explore in your codebase?</p>
                    </div>
                </div>
                
                <div class="input-container">
                    <textarea id="chat-input" placeholder="Ask about your codebase..." rows="1"></textarea>
                    <button id="send-button" onclick="sendMessage()">Send</button>
                </div>
            </div>

            <script>
                let currentTheme = 'dark';
                
                function toggleTheme() {{
                    const body = document.body;
                    const themeButton = document.querySelector('.theme-toggle');
                    
                    if (currentTheme === 'dark') {{
                        body.classList.add('light-theme');
                        themeButton.innerHTML = '☀️ Light';
                        currentTheme = 'light';
                    }} else {{
                        body.classList.remove('light-theme');
                        themeButton.innerHTML = '🌙 Dark';
                        currentTheme = 'dark';
                    }}
                    
                    localStorage.setItem('theme', currentTheme);
                }}
                
                // Load saved theme
                const savedTheme = localStorage.getItem('theme');
                if (savedTheme === 'light') {{
                    toggleTheme();
                }}
                
                function copyMessage(button) {{
                    const messageDiv = button.closest('.message');
                    const messageText = messageDiv.querySelector('div:last-child').innerText;
                    
                    navigator.clipboard.writeText(messageText).then(() => {{
                        button.textContent = 'Copied!';
                        button.classList.add('copied');
                        setTimeout(() => {{
                            button.textContent = 'Copy';
                            button.classList.remove('copied');
                        }}, 2000);
                    }});
                }}
                
                function copyCodeBlock(element) {{
                    const code = element.textContent;
                    navigator.clipboard.writeText(code).then(() => {{
                        // Visual feedback for code copy
                        element.style.backgroundColor = '#A3BE8C';
                        setTimeout(() => {{
                            element.style.backgroundColor = '';
                        }}, 1000);
                    }});
                }}
                
                // Add click handlers to code blocks
                document.addEventListener('click', function(e) {{
                    if (e.target.tagName === 'PRE') {{
                        copyCodeBlock(e.target);
                    }}
                }});
                
                function sendMessage() {{
                    const input = document.getElementById('chat-input');
                    const message = input.value.trim();
                    
                    if (!message) return;
                    
                    addUserMessage(message);
                    input.value = '';
                    
                    // Auto-resize textarea
                    input.style.height = '44px';
                    
                    // Send to backend
                    fetch('/chat', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{'message': message}})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        addAIMessage(data.response);
                    }})
                    .catch(error => {{
                        console.error('Error:', error);
                        addAIMessage('Sorry, there was an error processing your request.');
                    }});
                }}
                
                function addUserMessage(message) {{
                    const chatMessages = document.getElementById('chat-messages');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message user-message';
                    messageDiv.innerHTML = `
                        <div class="message-header">
                            <strong>👤 You</strong>
                        </div>
                        <div>${{escapeHtml(message)}}</div>
                    `;
                    chatMessages.appendChild(messageDiv);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }}
                
                function addAIMessage(message) {{
                    const chatMessages = document.getElementById('chat-messages');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message ai-message';
                    
                    // Convert markdown to HTML
                    const htmlContent = marked.parse(message);
                    
                    messageDiv.innerHTML = `
                        <div class="message-header">
                            <strong>🤖 CodeLve</strong>
                            <button class="copy-button" onclick="copyMessage(this)">Copy</button>
                        </div>
                        <div>${{htmlContent}}</div>
                    `;
                    
                    chatMessages.appendChild(messageDiv);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }}
                
                function escapeHtml(text) {{
                    const div = document.createElement('div');
                    div.textContent = text;
                    return div.innerHTML;
                }}
                
                // Auto-resize textarea
                const chatInput = document.getElementById('chat-input');
                chatInput.addEventListener('input', function() {{
                    this.style.height = '44px';
                    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
                }});
                
                // Enter to send message
                chatInput.addEventListener('keydown', function(e) {{
                    if (e.key === 'Enter' && !e.shiftKey) {{
                        e.preventDefault();
                        sendMessage();
                    }}
                }});
                
                // Focus input on load
                window.addEventListener('load', function() {{
                    chatInput.focus();
                }});
            </script>
        </body>
        </html>
        """

    def run_server(self):
        """Run the HTTP server"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        import urllib.parse

        class ChatHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(self.server.chat_ui.create_html().encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self):
                if self.path == '/chat':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    
                    try:
                        data = json.loads(post_data.decode('utf-8'))
                        message = data.get('message', '')
                        
                        # Get response from AI
                        if self.server.chat_ui.memory_manager.consolidated_codebase:
                            response = self.server.chat_ui.ai_client.analyze_codebase(
                                message, 
                                self.server.chat_ui.memory_manager.consolidated_codebase
                            )
                        else:
                            response = "⚠️ No codebase loaded. Please load a project first."
                        
                        # Add to conversation history
                        self.server.chat_ui.conversation.append({
                            'user': message,
                            'ai': response,
                            'timestamp': time.time()
                        })
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        
                        response_data = {'response': response}
                        self.wfile.write(json.dumps(response_data).encode('utf-8'))
                        
                    except Exception as e:
                        print(f"❌ Error processing request: {e}")
                        self.send_response(500)
                        self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                # Suppress default server logs
                pass

        # Start server
        server = HTTPServer(('localhost', self.port), ChatHandler)
        server.chat_ui = self
        
        print(f"🌐 Starting chat UI server on http://localhost:{self.port}")
        print("💡 The interface will open in your browser automatically")
        
        # Open browser
        threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{self.port}')).start()
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down chat UI server...")
            server.shutdown()

    def start(self):
        """Start the chat interface"""
        try:
            print("🚀 Initializing CodeLve Chat Interface...")
            
            if not self.memory_manager.consolidated_codebase:
                print("⚠️  No codebase loaded. Chat will have limited functionality.")
            else:
                print(f"✅ Codebase ready: {len(self.memory_manager.file_index)} files indexed")
            
            # Start server in a separate thread
            server_thread = threading.Thread(target=self.run_server, daemon=True)
            server_thread.start()
            
            # Keep main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                
        except Exception as e:
            print(f"❌ Failed to start chat UI: {e}")
            return False

    def cleanup(self):
        """Cleanup resources"""
        if self.server:
            self.server.shutdown()
        print("🧹 Chat UI cleanup complete")