const fs = require('fs');
const path = require('path');

// Extension to language mapping
const LANGUAGE_MAP = {
  '.js': 'javascript',
  '.jsx': 'javascript',
  '.ts': 'typescript',
  '.tsx': 'typescript',
  '.py': 'python',
  '.java': 'java',
  '.c': 'c',
  '.cpp': 'cpp',
  '.cs': 'csharp',
  '.go': 'go',
  '.rb': 'ruby',
  '.php': 'php',
  '.html': 'html',
  '.css': 'css',
  '.json': 'json',
  '.md': 'markdown',
  '.rs': 'rust',
  '.swift': 'swift',
  '.kt': 'kotlin',
  '.sh': 'bash',
  '.sql': 'sql',
  // Add more as needed
};

// Get language from file extension
function getLanguage(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return LANGUAGE_MAP[ext] || 'text';
}

// Check if a file is a text file
function isTextFile(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  // List of binary file extensions to skip
  const binaryExtensions = [
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', 
    '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.exe', '.dll', '.so', '.dylib',
    '.ttf', '.otf', '.woff', '.woff2',
    '.mp3', '.mp4', '.avi', '.mov', '.flv',
    '.sqlite', '.db'
  ];
  
  return !binaryExtensions.includes(ext);
}

// Get all files in a directory recursively
function getAllFiles(dirPath, options = {}) {
  const {
    ignored = [
      'node_modules', '.git', 'dist', 'build', 'out',
      '.DS_Store', 'Thumbs.db'
    ]
  } = options;
  
  let results = [];
  
  try {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dirPath, entry.name);
      
      // Skip ignored directories and files
      if (ignored.some(pattern => 
        entry.name === pattern || 
        entry.name.startsWith(pattern + '/') ||
        entry.name.endsWith('/' + pattern)
      )) {
        continue;
      }
      
      if (entry.isDirectory()) {
        results = results.concat(getAllFiles(fullPath, options));
      } else if (isTextFile(fullPath)) {
        results.push(fullPath);
      }
    }
  } catch (error) {
    console.error(`Error reading directory ${dirPath}:`, error);
  }
  
  return results;
}

// Read file content with error handling
function readFileContent(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (error) {
    console.error(`Error reading file ${filePath}:`, error);
    return null;
  }
}

// Chunk a file into segments
function chunkFile(filePath, maxChunkSize = 1000) {
  const content = readFileContent(filePath);
  if (!content) return [];
  
  const language = getLanguage(filePath);
  const lines = content.split('\n');
  const chunks = [];
  let currentChunk = [];
  let currentSize = 0;
  
  for (const line of lines) {
    // Rough estimate of tokens: ~4 chars per token
    const lineTokens = Math.ceil(line.length / 4);
    
    if (currentSize + lineTokens > maxChunkSize && currentChunk.length > 0) {
      chunks.push({
        path: filePath,
        content: currentChunk.join('\n'),
        language,
        startLine: chunks.length * maxChunkSize + 1,
        endLine: chunks.length * maxChunkSize + currentChunk.length
      });
      
      currentChunk = [line];
      currentSize = lineTokens;
    } else {
      currentChunk.push(line);
      currentSize += lineTokens;
    }
  }
  
  if (currentChunk.length > 0) {
    chunks.push({
      path: filePath,
      content: currentChunk.join('\n'),
      language,
      startLine: chunks.length * maxChunkSize + 1,
      endLine: chunks.length * maxChunkSize + currentChunk.length
    });
  }
  
  return chunks;
}

module.exports = {
  getAllFiles,
  readFileContent,
  chunkFile,
  getLanguage,
  isTextFile
};