const path = require('path');
const fs = require('./file-system');

// Default configuration for chunking
const DEFAULT_CONFIG = {
  maxChunkSize: 1000,
  overlap: 100,
  skipBinaryFiles: true,
  skipIgnoredDirs: true,
  ignoredDirs: [
    'node_modules', '.git', 'dist', 'build', 'out', 'bin',
    '.vscode', '.idea', '.vs', 'vendor', 'package-lock.json',
    'yarn.lock'
  ]
};

// Process a codebase directory into analyzable chunks
async function processCodebase(dirPath, config = {}) {
  // Merge default config with provided config
  const options = { ...DEFAULT_CONFIG, ...config };
  
  try {
    // Get all text files in the directory
    const allFiles = fs.getAllFiles(dirPath, {
      ignored: options.ignoredDirs
    });
    
    // Create chunks for each file
    let chunks = [];
    let fileMetadata = [];
    
    for (const filePath of allFiles) {
      // Skip very large files
      const stats = await fs.promises.stat(filePath);
      if (stats.size > 1024 * 1024 * 5) { // Skip files larger than 5MB
        console.log(`Skipping large file: ${filePath} (${stats.size} bytes)`);
        continue;
      }
      
      const relPath = path.relative(dirPath, filePath);
      const fileChunks = fs.chunkFile(filePath, options.maxChunkSize);
      
      chunks = chunks.concat(fileChunks);
      
      fileMetadata.push({
        path: relPath,
        absolutePath: filePath,
        language: fs.getLanguage(filePath),
        size: stats.size,
        chunks: fileChunks.length
      });
    }
    
    return {
      basePath: dirPath,
      files: fileMetadata,
      chunks,
      total: {
        files: fileMetadata.length,
        chunks: chunks.length
      }
    };
  } catch (error) {
    console.error('Error processing codebase:', error);
    throw error;
  }
}

// Create a simplified project overview
function createCodebaseOverview(codebaseData) {
  const { basePath, files, total } = codebaseData;
  
  // Count files by language
  const languageCounts = {};
  files.forEach(file => {
    const lang = file.language;
    languageCounts[lang] = (languageCounts[lang] || 0) + 1;
  });
  
  // Get top directories
  const directoryStructure = {};
  files.forEach(file => {
    const dir = path.dirname(file.path);
    if (dir === '.') return;
    
    const parts = dir.split(path.sep);
    let currentPath = '';
    
    for (const part of parts) {
      currentPath = currentPath ? path.join(currentPath, part) : part;
      directoryStructure[currentPath] = (directoryStructure[currentPath] || 0) + 1;
    }
  });
  
  // Sort directories by file count
  const topDirectories = Object.entries(directoryStructure)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([dir, count]) => ({ path: dir, files: count }));
  
  return {
    projectRoot: basePath,
    summary: {
      totalFiles: total.files,
      totalChunks: total.chunks,
      languageDistribution: languageCounts,
      topDirectories
    }
  };
}

// Find chunks that match a query
function findRelevantChunks(codebaseData, query, maxResults = 10) {
  const { chunks } = codebaseData;
  
  // Very simple relevance scoring - future: use vector search or more sophisticated matching
  const scoredChunks = chunks.map(chunk => {
    // Calculate a simple score based on keyword matching
    const content = chunk.content.toLowerCase();
    const queryWords = query.toLowerCase().split(/\s+/);
    
    let score = 0;
    queryWords.forEach(word => {
      if (content.includes(word)) {
        score += 1;
        
        // Boost score for exact matches
        const exactMatch = new RegExp(`\\b${word}\\b`, 'i');
        if (exactMatch.test(content)) {
          score += 0.5;
        }
      }
    });
    
    return {
      ...chunk,
      score
    };
  });
  
  // Sort by score and take top results
  return scoredChunks
    .filter(c => c.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, maxResults);
}

module.exports = {
  processCodebase,
  createCodebaseOverview,
  findRelevantChunks
};