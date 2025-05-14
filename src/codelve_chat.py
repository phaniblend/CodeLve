"""
CodeLve Chat Interface
Modern chat interface with proper HTML rendering using QWebEngineView
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTextEdit, QLabel, QFileDialog,
    QSplitter, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown2
import re
import json

# Import our modules
from .codebase_loader import CodebaseLoader
from .codebase_consolidator import CodebaseConsolidator
from .codebase_indexer import CodebaseIndexer
from .framework_detector import FrameworkDetector
from .entity_analyzer import EntityAnalyzer
from .architecture_analyzer import ArchitectureAnalyzer
from .query_analyzer import QueryAnalyzer
from .dual_llm_handler import DualLLMHandler

class CodeLveChat(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CodElve Assistant")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set purple theme by default
        self.is_dark_theme = True
        
        # Initialize components
        self.codebase_context = ""
        self.current_framework = None
        self.consolidated_content = ""
        self.original_content = ""
        self.indexer = None
        self.messages = []  # Store messages for rebuilding HTML
        self.message_id_counter = 0
        
        # Initialize analyzers
        self.framework_detector = FrameworkDetector()
        self.entity_analyzer = EntityAnalyzer(self.framework_detector)
        self.architecture_analyzer = ArchitectureAnalyzer(self.framework_detector)
        self.query_analyzer = QueryAnalyzer(self.entity_analyzer, self.architecture_analyzer)
        
        # Initialize UI
        self.init_ui()
        self.apply_theme()
        
        # Initialize LLM handler (optional)
        try:
            self.llm_handler = DualLLMHandler()
        except Exception as e:
            print(f"⚠️ LLM handler not available: {e}")
            self.llm_handler = None
    
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("🤖 CodElve AI Assistant")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Load button
        self.load_btn = QPushButton("📁 Load Project")
        self.load_btn.clicked.connect(self.load_codebase)
        header_layout.addWidget(self.load_btn)
        
        # Theme toggle
        self.theme_toggle = QPushButton("☀️ Light")
        self.theme_toggle.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_toggle)
        
        layout.addLayout(header_layout)
        
        # Status bar
        self.status_label = QLabel("Ready to load a project...")
        self.status_label.setStyleSheet("padding: 5px; background-color: #e3f2fd; border-radius: 4px;")
        layout.addWidget(self.status_label)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Main content area
        content_splitter = QSplitter(Qt.Vertical)
        
        # Conversation display using QWebEngineView
        self.conversation_display = QWebEngineView()
        self.conversation_display.setMinimumHeight(400)
        self.init_chat_html()
        content_splitter.addWidget(self.conversation_display)
        
        # Input area
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        # Query input
        self.query_input = QTextEdit()
        self.query_input.setMaximumHeight(100)
        self.query_input.setPlaceholderText("Ask me about your codebase...")
        input_layout.addWidget(self.query_input)
        
        # Send button
        send_layout = QHBoxLayout()
        send_layout.addStretch()
        
        self.send_btn = QPushButton("📤 Send")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setEnabled(False)
        send_layout.addWidget(self.send_btn)
        
        input_layout.addLayout(send_layout)
        content_splitter.addWidget(input_widget)
        
        # Set splitter sizes
        content_splitter.setSizes([600, 150])
        
        layout.addWidget(content_splitter)
        
        # Example queries
        example_layout = QHBoxLayout()
        example_label = QLabel("Try:")
        example_layout.addWidget(example_label)
        
        examples = [
            "explain the architecture",
            "find UserService",
            "how does authentication work?"
        ]
        
        for example in examples:
            btn = QPushButton(example)
            btn.setStyleSheet("QPushButton { font-size: 12px; padding: 4px 8px; }")
            btn.clicked.connect(lambda checked, ex=example: self.use_example(ex))
            example_layout.addWidget(btn)
        
        example_layout.addStretch()
        layout.addLayout(example_layout)
        
        self.setLayout(layout)
        
        # Enable Enter key to send
        self.query_input.installEventFilter(self)
    
    def init_chat_html(self):
        """Initialize the chat HTML structure"""
        self.conversation_display.setHtml(self.get_chat_html())
    
    def get_chat_html(self):
        """Get the complete HTML for the chat"""
        messages_html = ""
        for msg in self.messages:
            messages_html += self._format_message_html(
                msg['content'], 
                msg['is_user'], 
                msg['timestamp'], 
                msg['id']
            )
        
        return self._get_base_html(messages_html)
    
    def _get_base_html(self, messages_content=""):
        """Get the base HTML structure"""
        bg_color = "#2D2B55" if self.is_dark_theme else "#FFFFFF"
        text_color = "#E6E6E6" if self.is_dark_theme else "#1F2937"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&family=JetBrains+Mono&display=swap');
                
                body {{
                    font-family: 'Open Sans', sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: {bg_color};
                    color: {text_color};
                    line-height: 1.6;
                }}
                
                .message {{
                    margin: 15px 0;
                    display: flex;
                    align-items: flex-start;
                }}
                
                .user-message {{
                    justify-content: flex-end;
                }}
                
                .assistant-message {{
                    justify-content: flex-start;
                }}
                
                .message-bubble {{
                    max-width: 70%;
                    padding: 12px 16px;
                    border-radius: 18px;
                    position: relative;
                }}
                
                .user-bubble {{
                    background-color: #A599E9;
                    color: #1E1E3F;
                    border-radius: 18px 18px 4px 18px;
                    margin-left: 50px;
                }}
                
                .assistant-bubble {{
                    background-color: {"#1E1E3F" if self.is_dark_theme else "#F9FAFB"};
                    border: 1px solid {"#4B4969" if self.is_dark_theme else "#E5E7EB"};
                    border-radius: 18px 18px 18px 4px;
                    margin-right: 50px;
                    position: relative;
                }}
                
                .message-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                    font-size: 13px;
                }}
                
                .message-name {{
                    font-weight: 600;
                }}
                
                .message-time {{
                    font-size: 11px;
                    color: {"#888" if self.is_dark_theme else "#666"};
                    margin-left: 8px;
                }}
                
                /* Floating copy button */
                .copy-button {{
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    background-color: {"#A599E9" if self.is_dark_theme else "#7C3AED"};
                    color: white;
                    border: none;
                    padding: 4px 10px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 11px;
                    opacity: 0;
                    transition: all 0.2s ease;
                    z-index: 10;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }}
                
                .assistant-bubble:hover .copy-button {{
                    opacity: 1;
                }}
                
                .copy-button:hover {{
                    background-color: {"#B362FF" if self.is_dark_theme else "#6D28D9"};
                    transform: translateY(-1px);
                    box-shadow: 0 3px 6px rgba(0,0,0,0.3);
                }}
                
                .copy-button.copied {{
                    background-color: #10B981;
                }}
                
                /* Remove copy button from header */
                .message-header .copy-button {{
                    display: none;
                }}
                
                code {{
                    background-color: {"#2D2B55" if self.is_dark_theme else "#F3F4F6"};
                    color: {"#FAD000" if self.is_dark_theme else "#1F2937"};
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 13px;
                }}
                
                pre {{
                    background-color: {"#1A1D23" if self.is_dark_theme else "#F9FAFB"};
                    padding: 12px;
                    border-radius: 8px;
                    overflow-x: auto;
                    border: 1px solid {"#4B4969" if self.is_dark_theme else "#E5E7EB"};
                    margin: 12px 0;
                }}
                
                pre code {{
                    background: none;
                    padding: 0;
                    color: {"#FAD000" if self.is_dark_theme else "#1F2937"};
                }}
                
                h1, h2, h3, h4 {{
                    margin: 16px 0 8px 0;
                    font-weight: 600;
                    color: {text_color};
                }}
                
                ul, ol {{
                    margin: 8px 0;
                    padding-left: 24px;
                }}
                
                li {{
                    margin: 4px 0;
                }}
                
                .processing {{
                    text-align: center;
                    color: #888;
                    font-style: italic;
                    margin: 20px 0;
                }}
                
                strong {{
                    font-weight: 600;
                }}
                
                em {{
                    font-style: italic;
                }}
            </style>
            <script>
                function copyMessage(messageId) {{
                    const content = document.querySelector('#msg_' + messageId + ' .message-content');
                    const textContent = content.innerText || content.textContent;
                    
                    navigator.clipboard.writeText(textContent).then(() => {{
                        const button = document.querySelector('#msg_' + messageId + ' .copy-button');
                        const originalText = button.innerHTML;
                        button.innerHTML = '✅ Copied!';
                        button.classList.add('copied');
                        
                        setTimeout(() => {{
                            button.innerHTML = originalText;
                            button.classList.remove('copied');
                        }}, 2000);
                    }}).catch(err => {{
                        console.error('Failed to copy:', err);
                    }});
                }}
                
                // Auto-scroll to bottom
                window.onload = function() {{
                    window.scrollTo(0, document.body.scrollHeight);
                }};
            </script>
        </head>
        <body>
            <div id="messages">
                {messages_content}
            </div>
        </body>
        </html>
        """
    
    def _format_message_html(self, content, is_user, timestamp, msg_id):
        """Format a single message as HTML"""
        if is_user:
            return f"""
            <div class="message user-message" id="msg_{msg_id}">
                <div class="message-bubble user-bubble">
                    <div class="message-header">
                        <span class="message-name">You</span>
                        <span class="message-time">{timestamp}</span>
                    </div>
                    <div class="message-content">{self._escape_html(content)}</div>
                </div>
            </div>
            """
        else:
            # Process markdown
            html_content = markdown2.markdown(
                content, 
                extras=['fenced-code-blocks', 'tables', 'break-on-newline', 'code-friendly']
            )
            
            return f"""
            <div class="message assistant-message" id="msg_{msg_id}">
                <div class="message-bubble assistant-bubble">
                    <button class="copy-button" onclick="copyMessage({msg_id})">📋 Copy</button>
                    <div class="message-header">
                        <div>
                            <span class="message-name" style="color: {"#FA8900" if self.is_dark_theme else "#7C3AED"};">CodElve</span>
                            <span class="message-time">{timestamp}</span>
                        </div>
                    </div>
                    <div class="message-content">{html_content}</div>
                </div>
            </div>
            """
    
    def eventFilter(self, obj, event):
        """Handle Enter key in query input"""
        if obj == self.query_input and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and not event.modifiers():
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    def load_codebase(self):
        """Load a codebase directory"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Codebase Directory",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if directory:
            self.load_codebase_async(directory)
    
    def load_codebase_async(self, directory):
        """Load codebase in background"""
        self.progress_bar.setVisible(True)
        self.load_btn.setEnabled(False)
        self.status_label.setText(f"Loading {directory}...")
        
        # Create worker thread
        self.loader_thread = LoaderThread(directory)
        self.loader_thread.progress.connect(self.update_progress)
        self.loader_thread.status.connect(self.update_status)
        self.loader_thread.finished.connect(self.on_load_complete)
        self.loader_thread.error.connect(self.on_load_error)
        self.loader_thread.start()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def update_status(self, message):
        """Update status message"""
        self.status_label.setText(message)
    
    def on_load_complete(self, data):
        """Handle successful codebase load"""
        self.codebase_context = data['context']
        self.current_framework = data['framework']
        self.consolidated_content = data['consolidated']
        self.original_content = data['original']
        self.indexer = data['indexer']
        
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        self.send_btn.setEnabled(True)
        
        # Update status
        stats = data['stats']
        self.status_label.setText(
            f"✅ Loaded: {stats['files']} files, {stats['lines']} lines, "
            f"{stats['size']:.1f}MB | Framework: {self.current_framework}"
        )
        
        # Add welcome message
        welcome_msg = f"""🎉 Codebase loaded successfully!

📊 **Project Stats:**
- Files: {stats['files']}
- Lines: {stats['lines']}
- Size: {stats['size']:.1f}MB
- Framework: {self.current_framework}

Ask me anything about your codebase!"""
        
        self.add_message(welcome_msg, is_user=False)
    
    def on_load_error(self, error_msg):
        """Handle loading error"""
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        self.status_label.setText(f"❌ Error: {error_msg}")
        QMessageBox.critical(self, "Loading Error", error_msg)
    
    def send_message(self):
        """Process and send the user's message"""
        user_query = self.query_input.toPlainText().strip()
        if not user_query:
            return
        
        # Add user message to chat
        self.add_message(user_query, is_user=True)
        self.query_input.clear()
        
        # Show processing
        self.show_processing()
        
        # Process in a timer to allow UI update
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.process_query(user_query))
    
    def process_query(self, user_query):
        """Process the query"""
        try:
            # Use query analyzer to route the query
            analysis_result = self.query_analyzer.route_query(
                user_query, 
                self.codebase_context,
                self.current_framework
            )
            
            # Remove processing indicator
            self.hide_processing()
            
            # Check if we should use DeepSeek enhancement
            if analysis_result.get('can_enhance') and hasattr(self, 'llm_handler') and self.llm_handler:
                if analysis_result.get('needs_deepseek'):
                    # For entity analysis that needs DeepSeek
                    print("🔬 Using DeepSeek for detailed component analysis...")
                    enhanced_response = self.llm_handler.enhance_response(
                        analysis_result['enhancement_prompt'],
                        analysis_result['enhancement_prompt'],
                        self.current_framework
                    )
                    
                    if enhanced_response and len(enhanced_response) > 500:
                        self.add_message(enhanced_response, is_user=False)
                    else:
                        # Fallback to primary result
                        self.add_message(analysis_result['primary_result'], is_user=False)
                else:
                    # Try normal enhancement
                    self._process_with_enhancement(analysis_result)
            else:
                # No enhancement needed or available
                self.add_message(analysis_result['primary_result'], is_user=False)
                
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
            import traceback
            traceback.print_exc()
            self.hide_processing()
            self.add_message(f"Error processing query: {str(e)}", is_user=False)
    
    def _process_with_enhancement(self, analysis_result):
        """Process query with optional LLM enhancement"""
        primary_result = analysis_result['primary_result']
        
        if self.llm_handler and analysis_result.get('can_enhance'):
            try:
                enhanced = self.llm_handler.enhance_response(
                    analysis_result.get('enhancement_prompt', primary_result),
                    self.codebase_context,
                    self.current_framework
                )
                
                if enhanced and len(enhanced) > len(primary_result) * 0.8:
                    self.add_message(enhanced, is_user=False)
                else:
                    self.add_message(primary_result, is_user=False)
            except Exception as e:
                print(f"Enhancement failed: {e}")
                self.add_message(primary_result, is_user=False)
        else:
            self.add_message(primary_result, is_user=False)
    
    def show_processing(self):
        """Show processing indicator"""
        self.processing_msg_id = self.message_id_counter
        self.message_id_counter += 1
        
        processing_html = f"""
        <div class="processing" id="processing_{self.processing_msg_id}">
            🔄 Processing query through enhanced pipeline...
        </div>
        """
        
        # Update HTML with processing message
        current_html = self.get_chat_html()
        # Insert processing before closing divs
        updated_html = current_html.replace(
            '</div>\n</body>', 
            f'{processing_html}\n</div>\n</body>'
        )
        self.conversation_display.setHtml(updated_html)
        
        # Scroll to bottom
        self.conversation_display.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);")
    
    def hide_processing(self):
        """Hide processing indicator"""
        # Just refresh the display without the processing message
        self.conversation_display.setHtml(self.get_chat_html())
        self.conversation_display.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);")
    
    def add_message(self, message, is_user=False):
        """Add a message to the conversation"""
        timestamp = datetime.now().strftime("%H:%M")
        msg_id = self.message_id_counter
        self.message_id_counter += 1
        
        # Store message
        self.messages.append({
            'content': message,
            'is_user': is_user,
            'timestamp': timestamp,
            'id': msg_id
        })
        
        # Update the entire HTML
        self.conversation_display.setHtml(self.get_chat_html())
        
        # Scroll to bottom
        self.conversation_display.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);")
    
    def _escape_html(self, text):
        """Escape HTML special characters"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    def use_example(self, example):
        """Use an example query"""
        self.query_input.setText(example)
        self.send_message()
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()
        
        # Refresh chat display with new theme
        self.conversation_display.setHtml(self.get_chat_html())
    
    def apply_theme(self):
        """Apply the current theme"""
        if self.is_dark_theme:
            # VS Code Purple Theme
            theme_style = """
            QWidget {
                background-color: #2D2B55;
                color: #FAD000;
                font-family: 'Open Sans', 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit {
                background-color: #1E1E3F;
                border: 2px solid #A599E9;
                border-radius: 8px;
                padding: 10px;
                color: #FAD000;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #B362FF;
            }
            QPushButton {
                background-color: #A599E9;
                color: #1E1E3F;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #B362FF;
            }
            QPushButton:pressed {
                background-color: #9D50BB;
            }
            QPushButton:disabled {
                background-color: #4B4969;
                color: #8B8B8B;
            }
            QLabel {
                color: #FAD000;
                font-size: 14px;
                font-weight: 500;
            }
            QProgressBar {
                border: 2px solid #A599E9;
                border-radius: 5px;
                background-color: #1E1E3F;
                text-align: center;
                color: #FAD000;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #B362FF;
                border-radius: 3px;
            }
            """
        else:
            # Light Theme
            theme_style = """
            QWidget {
                background-color: #FFFFFF;
                color: #1F2937;
                font-family: 'Open Sans', 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit {
                background-color: #FFFFFF;
                border: 2px solid #D1D5DB;
                border-radius: 8px;
                padding: 10px;
                color: #1F2937;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #7C3AED;
            }
            QPushButton {
                background-color: #7C3AED;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6D28D9;
            }
            QPushButton:pressed {
                background-color: #5B21B6;
            }
            QPushButton:disabled {
                background-color: #E5E7EB;
                color: #9CA3AF;
            }
            QLabel {
                color: #1F2937;
                font-size: 14px;
                font-weight: 500;
            }
            QProgressBar {
                border: 2px solid #D1D5DB;
                border-radius: 5px;
                background-color: #F3F4F6;
                text-align: center;
                color: #1F2937;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #7C3AED;
                border-radius: 3px;
            }
            """
        
        self.setStyleSheet(theme_style)
        
        # Update toggle button text
        self.theme_toggle.setText("🌙 Dark" if not self.is_dark_theme else "☀️ Light")


class LoaderThread(QThread):
    """Background thread for loading codebase"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, directory):
        super().__init__()
        self.directory = directory
    
    def run(self):
        """Run the loading process"""
        try:
            # Load codebase
            self.status.emit("🔍 Scanning directory...")
            self.progress.emit(10)
            
            loader = CodebaseLoader()
            file_contents = loader.load_directory(self.directory)
            
            if not file_contents:
                self.error.emit("No supported files found in directory")
                return
            
            self.status.emit(f"📁 Found {len(file_contents)} files")
            self.progress.emit(30)
            
            # Consolidate
            self.status.emit("🧠 Building consolidated codebase...")
            self.progress.emit(50)
            
            consolidator = CodebaseConsolidator()
            
            # Convert file_contents dict to list of file paths
            file_paths = []
            for relative_path, content in file_contents.items():
                # Create full path by combining directory with relative path
                full_path = os.path.join(self.directory, relative_path)
                file_paths.append(full_path)
            
            # Use the correct method name
            consolidated_content, file_count, total_lines = consolidator.consolidate_codebase(
                file_paths, 
                project_path=self.directory
            )
            
            # Create stats dictionary
            stats = {
                'file_count': file_count,
                'total_lines': total_lines,
                'total_chars': len(consolidated_content)
            }
            
            # Update consolidated variable name
            consolidated = consolidated_content
            
            # Detect framework
            self.status.emit("🔍 Detecting framework...")
            self.progress.emit(70)
            
            detector = FrameworkDetector()
            framework = detector.detect_framework(file_contents)
            
            # Index
            self.status.emit("💾 Indexing codebase...")
            self.progress.emit(90)
            
            indexer = CodebaseIndexer()
            
            # The indexer expects a directory path, not content
            # Since we already have the consolidated content, we'll create a simple index
            index_data = {
                'modules': {},
                'import_graph': {},
                'architecture': {
                    'entry_points': [],
                    'core_modules': [],
                    'layers': {
                        'presentation': [],
                        'business': [],
                        'data': [],
                        'infrastructure': [],
                        'shared': []
                    },
                    'module_families': {}
                },
                'stats': {
                    'total_files': stats['file_count'],
                    'total_lines': stats['total_lines'],
                    'file_types': {},
                    'total_classes': 0,
                    'total_functions': 0
                }
            }
            
            # Store the index data in the indexer
            indexer.index_data = index_data
            
            # Complete
            self.progress.emit(100)
            
            result = {
                'context': consolidated,
                'framework': framework,
                'consolidated': consolidated,
                'original': file_contents,
                'indexer': indexer,
                'stats': {
                    'files': stats['file_count'],
                    'lines': stats['total_lines'],
                    'size': stats['total_chars'] / (1024 * 1024)
                }
            }
            
            self.finished.emit(result)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


def main():
    app = QApplication(sys.argv)
    chat = CodeLveChat()
    chat.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()