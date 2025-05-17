# CodeLve Architecture Overview

## Component Architecture
+-------------------------------+
|      Electron Application     |
|                               |
|  +----------+  +-----------+  |
|  |          |  |           |  |
|  |  Lite XL |  |   Chat    |  |
|  |  Bridge  |  |   Panel   |  |
|  |          |  |           |  |
|  +----^-----+  +-----^-----+  |
+-------|--------------|--------+
|              |
v              v
+----------------+ +------------------+
| Lite XL Editor | | LlamaService     |
| (External Proc)| | (llama.cpp API)  |
+----------------+ +------------------+
|
v
+---------------+
| Language Model|
| (GGUF Format) |
+---------------+

## Component Descriptions

### Electron Application
- Main application container using Electron framework
- Manages window, UI, and component coordination
- Provides the split-panel interface

### Chat Panel
- Handles user interaction for code queries
- Displays AI-generated responses with proper formatting
- Communicates with LlamaService for inference

### Lite XL Bridge
- Manages communication with the Lite XL editor
- Handles file operations and editor state
- Provides code context from editor to AI

### LlamaService
- Integrates with llama.cpp via llama-node package
- Manages language model loading and inference
- Processes queries with code context

### Lite XL Editor
- Lightweight, customizable code editor (MIT license)
- Runs as separate process
- Modified with custom plugin for CodeLve integration

### Language Model
- GGUF format model file (e.g., Mistral, CodeGemma)
- Stored locally in user config directory
- Used by llama.cpp for inference

## Data Flow

1. **Editor to AI Flow**:
   - User edits code in Lite XL
   - Editor plugin notifies CodeLve of file changes
   - coditor extracts code context
   - Code context is provided to LlamaService with query

2. **AI to Editor Flow**:
   - LlamaService processes query with code context
   - Generated response displayed in Chat Panel
   - User can apply suggestions back to editor
   - coditor can create/modify files based on AI suggestions

## Directory Structure
/CodeLve
/src
/ai
- llama-service.js   # LlamaService implementation
/chat
- chat-panel.js      # Chat UI component
- chat-panel.css     # Chat styling
/core
- main.js            # Main Electron process
- preload.js         # Electron preload script
- process-manager.js # Process handling
/editor
- lite-xl-bridge.js  # Lite XL integration
/ui
- main-layout.js     # Main UI layout
- main-layout.css    # UI styling
/utils
- file-handler.js    # File system utilities
/docs
- architecture.md    # This document
/resources
/images                # Application icons
/libs
/lite-xl             # Lite XL plugins/config
/scripts
- download-models.js   # Model download utility
- llama-test.js        # Integration test
- setup.js             # Setup script

## Development Workflow

1. **Setup Environment**:
   - Install Node.js dependencies: `npm install`
   - Run setup script: `node scripts/setup.js`
   - Download language model: `node scripts/download-models.js mistral`

2. **Test Integration**:
   - Test llama.cpp: `node scripts/llama-test.js`
   - Verify Lite XL integration

3. **Run Application**:
   - Development mode: `npm start`
   - Build package: `npm run build`

4. **Debugging**:
   - Check Electron logs
   - Test LlamaService separately
   - Verify Lite XL plugin functionality