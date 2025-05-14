"""
Simplified Chat UI for CodeLve using Flet
"""
import flet as ft
import asyncio
from datetime import datetime
import os
from typing import Optional
from codebase_loader import CodebaseLoader
from dual_llm_handler import DualLLMHandler
import logging

logger = logging.getLogger(__name__)

class SimplifiedChatUI:
    def __init__(self, codelve_chat=None):
        self.codelve_chat = codelve_chat
        self.page = None
        self.chat_messages = None
        self.user_input = None
        self.send_button = None
        self.project_path_input = None
        self.load_project_button = None
        self.project_info = None
        self.main_content = None
        self.project_loaded = False
        
    def create_message(self, sender: str, message: str, is_user: bool = False):
        """Create a chat message component"""
        # Create message container
        message_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    sender,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE if is_user else ft.colors.GREEN
                ),
                ft.Markdown(
                    message,
                    selectable=True,
                    extension_set="gitHubWeb",
                    code_theme="atom-one-dark",
                    code_style=ft.TextStyle(font_family="Courier New")
                )
            ]),
            padding=10,
            border_radius=10,
            bgcolor=ft.colors.BLUE_50 if is_user else ft.colors.GREEN_50,
            margin=ft.margin.only(bottom=10, left=50 if is_user else 0, right=0 if is_user else 50)
        )
        
        return message_container
    
    async def load_project(self, e):
        """Load a project from the specified path"""
        project_path = self.project_path_input.value.strip()
        
        if not project_path:
            await self.show_error("Please enter a project path")
            return
        
        if not os.path.exists(project_path):
            await self.show_error(f"Path '{project_path}' does not exist")
            return
        
        if not os.path.isdir(project_path):
            await self.show_error(f"Path '{project_path}' is not a directory")
            return
        
        # Disable inputs during loading
        self.project_path_input.disabled = True
        self.load_project_button.disabled = True
        self.load_project_button.text = "Loading..."
        await self.page.update_async()
        
        try:
            # Load the codebase
            loader = CodebaseLoader(project_path)
            
            # Update status
            self.project_info.value = "🔍 Scanning files..."
            await self.page.update_async()
            
            files = loader.scan_files()
            
            if not files:
                await self.show_error("No supported files found in the project")
                return
            
            # Update status
            self.project_info.value = f"📥 Loading {len(files)} files..."
            await self.page.update_async()
            
            file_contents = loader.load_files(files)
            
            # Update status
            self.project_info.value = "🔄 Consolidating codebase..."
            await self.page.update_async()
            
            consolidated_code, stats = loader.consolidate_files(file_contents)
            
            # Initialize Dual LLM Handler if not already done
            if not hasattr(self, 'dual_llm_handler'):
                self.dual_llm_handler = DualLLMHandler()
            
            # Create CodeLve chat instance
            from codelve_chat import CodeLveChat
            self.codelve_chat = CodeLveChat(
                consolidated_code=consolidated_code,
                project_path=project_path,
                dual_llm_handler=self.dual_llm_handler
            )
            
            # Update UI
            self.project_loaded = True
            self.project_info.value = f"✅ Project loaded: {os.path.basename(project_path)} ({stats['total_files']} files, {stats['total_lines']} lines)"
            
            # Show welcome message
            welcome_msg = f"""🎉 **Codebase loaded successfully!**

📊 **Project Stats:**
- Files: {stats['total_files']}
- Lines: {stats['total_lines']}
- Size: {stats['total_chars'] / 1024 / 1024:.1f}MB
- Framework: {self._detect_framework(consolidated_code)}

Ask me anything about your codebase!"""
            
            self.chat_messages.controls.append(
                self.create_message("CodeLve", welcome_msg, is_user=False)
            )
            
            # Enable chat inputs
            self.user_input.disabled = False
            self.send_button.disabled = False
            
            # Keep project loading inputs visible but update button
            self.load_project_button.text = "Load Different Project"
            self.load_project_button.disabled = False
            self.project_path_input.disabled = False
            
            await self.page.update_async()
            
        except Exception as e:
            await self.show_error(f"Error loading project: {str(e)}")
            
            # Re-enable inputs
            self.project_path_input.disabled = False
            self.load_project_button.disabled = False
            self.load_project_button.text = "Load Project"
            await self.page.update_async()
    
    def _detect_framework(self, consolidated_code: str) -> str:
        """Simple framework detection"""
        if 'import React' in consolidated_code or 'from react' in consolidated_code:
            return 'React' + ('/TypeScript' if '.tsx' in consolidated_code else '/JavaScript')
        elif 'import Vue' in consolidated_code or 'from vue' in consolidated_code:
            return 'Vue.js'
        elif 'from django' in consolidated_code:
            return 'Django'
        elif 'from flask' in consolidated_code:
            return 'Flask'
        else:
            return 'Python' if '.py' in consolidated_code else 'Unknown'
    
    async def show_error(self, message: str):
        """Show error message"""
        self.project_info.value = f"❌ {message}"
        self.project_info.color = ft.colors.RED
        await self.page.update_async()
        
        # Reset color after 3 seconds
        await asyncio.sleep(3)
        self.project_info.color = None
        await self.page.update_async()
    
    async def send_message(self, e):
        """Handle sending a message"""
        if not self.project_loaded:
            await self.show_error("Please load a project first")
            return
        
        if not self.user_input.value.strip():
            return
        
        user_message = self.user_input.value.strip()
        
        # Add user message to chat
        self.chat_messages.controls.append(
            self.create_message("You", user_message, is_user=True)
        )
        
        # Clear input and disable while processing
        self.user_input.value = ""
        self.user_input.disabled = True
        self.send_button.disabled = True
        await self.page.update_async()
        
        try:
            # Get response from CodeLve
            response = self.codelve_chat.process_query(user_message)
            
            # Add response to chat
            self.chat_messages.controls.append(
                self.create_message("CodeLve", response, is_user=False)
            )
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.chat_messages.controls.append(
                self.create_message("CodeLve", error_msg, is_user=False)
            )
        
        # Re-enable inputs
        self.user_input.disabled = False
        self.send_button.disabled = False
        self.user_input.focus()
        
        # Scroll to bottom
        await self.chat_messages.scroll_to_async(offset=-1, duration=300)
        await self.page.update_async()
    
    async def main(self, page: ft.Page):
        """Main UI setup"""
        self.page = page
        page.title = "CodeLve - AI Codebase Assistant"
        page.theme_mode = ft.ThemeMode.LIGHT
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.CODE, size=40, color=ft.colors.BLUE),
                ft.Text("CodeLve", size=30, weight=ft.FontWeight.BOLD),
                ft.Text("AI-Powered Codebase Assistant", size=16)
            ]),
            padding=20,
            bgcolor=ft.colors.BLUE_50
        )
        
        # Project loading section
        self.project_path_input = ft.TextField(
            label="Project Path",
            hint_text="Enter the path to your project (e.g., D:\\carb\\test\\carb-carl-frontend)",
            expand=True,
            on_submit=self.load_project
        )
        
        self.load_project_button = ft.ElevatedButton(
            "Load Project",
            icon=ft.icons.FOLDER_OPEN,
            on_click=self.load_project
        )
        
        self.project_info = ft.Text(
            "No project loaded",
            size=14,
            italic=True
        )
        
        project_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    self.project_path_input,
                    self.load_project_button
                ]),
                self.project_info
            ]),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            margin=ft.margin.only(bottom=20)
        )
        
        # Chat messages area
        self.chat_messages = ft.ListView(
            expand=True,
            spacing=10,
            padding=ft.padding.all(20),
            auto_scroll=True
        )
        
        # Input area
        self.user_input = ft.TextField(
            label="Ask about your codebase...",
            multiline=True,
            min_lines=1,
            max_lines=5,
            expand=True,
            on_submit=self.send_message,
            disabled=True  # Disabled until project is loaded
        )
        
        self.send_button = ft.IconButton(
            icon=ft.icons.SEND,
            icon_color=ft.colors.BLUE,
            on_click=self.send_message,
            disabled=True  # Disabled until project is loaded
        )
        
        input_row = ft.Row([
            self.user_input,
            self.send_button
        ])
        
        # Main content
        self.main_content = ft.Column([
            header,
            project_section,
            ft.Container(
                content=self.chat_messages,
                expand=True,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=10
            ),
            ft.Container(
                content=input_row,
                padding=10
            )
        ])
        
        page.add(self.main_content)
        
        # Show initial message
        self.chat_messages.controls.append(
            self.create_message(
                "CodeLve", 
                "👋 Welcome to CodeLve!\n\nPlease load a project using the input above to get started.",
                is_user=False
            )
        )
        
        await page.update_async()

def run_ui():
    """Run the UI as a desktop application"""
    ui = SimplifiedChatUI()
    ft.app(
        target=ui.main,
        view=ft.AppView.FLET_APP  # This makes it a desktop app
    )