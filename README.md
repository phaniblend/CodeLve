# CodeLve Desktop

A cross-platform desktop application for intelligent code analysis using local LLMs via Ollama.

## Features

- Analyze local codebases using open-source LLMs with Ollama
- Smart code chunking and indexing
- Interactive chat interface for codebase queries
- Syntax highlighting and markdown support
- Session management for resuming conversations
- Light/dark mode and customizable prompts
- Completely offline after initial model setup

## Requirements

- Node.js 18+
- Ollama installed locally 
- System with AVX2 support (for running Ollama)
- 8-16 GB RAM recommended

## Development

```bash
# Install dependencies
npm install

# Run the app in development mode
npm run dev