// Debug logger for CodeLve
const fs = require('fs');
const path = require('path');

class DebugLogger {
  constructor() {
    this.logPath = path.join(process.cwd(), 'codelve-debug.log');
    this.enabled = true;
    
    // Clear log file on start
    if (this.enabled) {
      try {
        fs.writeFileSync(this.logPath, 'CodeLve Debug Log\n=================\n\n', 'utf8');
        this.log('Debug logger initialized');
      } catch (error) {
        console.error('Unable to create debug log file:', error);
        this.enabled = false;
      }
    }
  }
  
  log(message, data = null) {
    if (!this.enabled) return;
    
    try {
      const timestamp = new Date().toISOString();
      let logMessage = `[${timestamp}] ${message}\n`;
      
      if (data) {
        if (typeof data === 'object') {
          logMessage += JSON.stringify(data, null, 2) + '\n';
        } else {
          logMessage += data + '\n';
        }
      }
      
      fs.appendFileSync(this.logPath, logMessage + '\n', 'utf8');
    } catch (error) {
      console.error('Error writing to debug log:', error);
    }
  }
}

module.exports = new DebugLogger();