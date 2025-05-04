const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Database configuration
const DB_DIR = path.join(process.cwd(), 'data');
const DB_PATH = path.join(DB_DIR, 'codelve.db');

// Ensure data directory exists
if (!fs.existsSync(DB_DIR)) {
  fs.mkdirSync(DB_DIR, { recursive: true });
}

// Initialize database connection
const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error('Error connecting to database:', err);
    return;
  }
  console.log('Connected to SQLite database');
  
  // Create tables if they don't exist
  initializeDatabase();
});

// Initialize database schema
function initializeDatabase() {
  // Create sessions table
  db.run(`
    CREATE TABLE IF NOT EXISTS sessions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      codebase_path TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);
  
  // Create messages table
  db.run(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id INTEGER NOT NULL,
      content TEXT NOT NULL,
      sender TEXT NOT NULL,
      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
    )
  `);
  
  // Create codebase_files table
  db.run(`
    CREATE TABLE IF NOT EXISTS codebase_files (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id INTEGER NOT NULL,
      path TEXT NOT NULL,
      language TEXT NOT NULL,
      indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
    )
  `);
}

// Session management
async function createSession(name, codebasePath) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT INTO sessions (name, codebase_path)
      VALUES (?, ?)
    `);
    
    stmt.run(name, codebasePath, function(err) {
      if (err) {
        reject(err);
        return;
      }
      
      resolve({
        id: this.lastID,
        name,
        codebasePath,
        createdAt: new Date()
      });
    });
    
    stmt.finalize();
  });
}

async function getSessions() {
  return new Promise((resolve, reject) => {
    db.all(`
      SELECT id, name, codebase_path, created_at, updated_at
      FROM sessions
      ORDER BY updated_at DESC
    `, (err, rows) => {
      if (err) {
        reject(err);
        return;
      }
      
      resolve(rows);
    });
  });
}

async function getSession(id) {
  return new Promise((resolve, reject) => {
    db.get(`
      SELECT id, name, codebase_path, created_at, updated_at
      FROM sessions
      WHERE id = ?
    `, [id], (err, row) => {
      if (err) {
        reject(err);
        return;
      }
      
      resolve(row);
    });
  });
}

async function updateSessionTimestamp(id) {
  return new Promise((resolve, reject) => {
    db.run(`
      UPDATE sessions
      SET updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `, [id], function(err) {
      if (err) {
        reject(err);
        return;
      }
      
      resolve({ updated: this.changes > 0 });
    });
  });
}

// Message management
async function saveMessage(sessionId, content, sender) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT INTO messages (session_id, content, sender)
      VALUES (?, ?, ?)
    `);
    
    stmt.run(sessionId, content, sender, function(err) {
      if (err) {
        reject(err);
        return;
      }
      
      // Update session timestamp
      updateSessionTimestamp(sessionId).catch(console.error);
      
      resolve({
        id: this.lastID,
        sessionId,
        content,
        sender,
        timestamp: new Date()
      });
    });
    
    stmt.finalize();
  });
}

async function getSessionMessages(sessionId) {
  return new Promise((resolve, reject) => {
    db.all(`
      SELECT id, content, sender, timestamp
      FROM messages
      WHERE session_id = ?
      ORDER BY timestamp ASC
    `, [sessionId], (err, rows) => {
      if (err) {
        reject(err);
        return;
      }
      
      resolve(rows);
    });
  });
}

// Codebase files management
async function saveCodebaseFile(sessionId, filePath, language) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT INTO codebase_files (session_id, path, language)
      VALUES (?, ?, ?)
    `);
    
    stmt.run(sessionId, filePath, language, function(err) {
      if (err) {
        reject(err);
        return;
      }
      
      resolve({
        id: this.lastID,
        sessionId,
        path: filePath,
        language
      });
    });
    
    stmt.finalize();
  });
}

// Close database connection on process exit
process.on('exit', () => {
  db.close((err) => {
    if (err) {
      console.error('Error closing database:', err);
    } else {
      console.log('Database connection closed');
    }
  });
});

module.exports = {
  createSession,
  getSessions,
  getSession,
  saveMessage,
  getSessionMessages,
  saveCodebaseFile
};