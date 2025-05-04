const express = require('express');
const axios = require('axios');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3001;

// Middleware
app.use(express.json());
app.use(cors());

// Check Ollama status
app.get('/api/status', async (req, res) => {
  try {
    const response = await axios.get('http://localhost:11434/api/version');
    res.json({ running: true, version: response.data.version });
  } catch (error) {
    res.json({ running: false, error: error.message });
  }
});

// Get available models from Ollama
app.get('/api/models', async (req, res) => {
  try {
    const response = await axios.get('http://localhost:11434/api/tags');
    res.json(response.data.models || []);
  } catch (error) {
    console.error('Error getting models:', error);
    res.status(500).json({ error: error.message });
  }
});

// Send chat message to Ollama
app.post('/api/chat', async (req, res) => {
  const { prompt, model, temperature, maxTokens } = req.body;
  
  try {
    const response = await axios.post('http://localhost:11434/api/generate', {
      model: model || 'mistral',
      prompt,
      temperature: temperature || 0.7,
      max_tokens: maxTokens || 4000,
      stream: false
    });
    
    res.json({ response: response.data.response });
  } catch (error) {
    console.error('Error calling Ollama:', error);
    res.status(500).json({ error: error.message });
  }
});

// File system operations
app.post('/api/list-directory', (req, res) => {
  const { path: dirPath } = req.body;
  
  try {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    const files = entries.map(entry => ({
      name: entry.name,
      isDirectory: entry.isDirectory(),
      path: path.join(dirPath, entry.name)
    }));
    
    res.json({ files });
  } catch (error) {
    console.error('Error listing directory:', error);
    res.status(500).json({ error: error.message });
  }
});

// Read file content
app.post('/api/read-file', (req, res) => {
  const { path: filePath } = req.body;
  
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    res.json({ content });
  } catch (error) {
    console.error('Error reading file:', error);
    res.status(500).json({ error: error.message });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});