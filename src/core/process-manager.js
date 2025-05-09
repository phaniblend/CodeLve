/**
 * Process Manager for CodeLve
 * 
 * Handles starting, monitoring, and stopping external processes
 * required by the application (VSCodium, Ollama, etc.)
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

class ProcessManager {
  constructor() {
    this.processes = new Map();
    this.isShuttingDown = false;
  }

  /**
   * Start a managed process
   * 
   * @param {string} name Unique name for the process
   * @param {string} command Command to execute
   * @param {Array<string>} args Command arguments
   * @param {Object} options Spawn options
   * @returns {Promise<boolean>} True if started successfully
   */
  async startProcess(name, command, args, options = {}) {
    if (this.processes.has(name)) {
      console.log(`Process ${name} is already running`);
      return true;
    }

    return new Promise((resolve) => {
      try {
        console.log(`Starting process: ${name} (${command} ${args.join(' ')})`);
        
        // Default options
        const defaultOptions = {
          stdio: 'pipe',
          detached: false
        };
        
        // Merge options
        const mergedOptions = { ...defaultOptions, ...options };
        
        // Spawn the process
        const process = spawn(command, args, mergedOptions);
        
        // Store reference
        this.processes.set(name, {
          name,
          process,
          command,
          args,
          options: mergedOptions,
          startTime: Date.now()
        });
        
        // Handle output
        if (process.stdout) {
          process.stdout.on('data', (data) => {
            console.log(`[${name}] ${data.toString().trim()}`);
          });
        }
        
        if (process.stderr) {
          process.stderr.on('data', (data) => {
            console.error(`[${name}] ERROR: ${data.toString().trim()}`);
          });
        }
        
        // Handle process exit
        process.on('exit', (code) => {
          console.log(`Process ${name} exited with code ${code}`);
          
          if (!this.isShuttingDown) {
            this.processes.delete(name);
          }
        });
        
        // Handle process error
        process.on('error', (err) => {
          console.error(`Error in process ${name}:`, err);
          this.processes.delete(name);
          resolve(false);
        });
        
        // Resolve when the process has started
        process.on('spawn', () => {
          console.log(`Process ${name} spawned successfully`);
          resolve(true);
        });
        
        // Resolve with false if the process doesn't start within 5 seconds
        setTimeout(() => {
          if (!process.exitCode && !process.killed) {
            resolve(true);
          } else {
            console.error(`Process ${name} failed to start within timeout`);
            resolve(false);
          }
        }, 5000);
      } catch (error) {
        console.error(`Failed to start process ${name}:`, error);
        resolve(false);
      }
    });
  }

  /**
   * Stop a managed process
   * 
   * @param {string} name Name of the process to stop
   * @returns {Promise<boolean>} True if stopped successfully
   */
  async stopProcess(name) {
    const processInfo = this.processes.get(name);
    if (!processInfo) {
      console.log(`Process ${name} is not running`);
      return true;
    }

    return new Promise((resolve) => {
      try {
        const { process } = processInfo;
        
        // Set a timeout to force kill if it doesn't exit gracefully
        const forceKillTimeout = setTimeout(() => {
          console.log(`Force killing process ${name}`);
          if (process.pid) {
            try {
              process.kill('SIGKILL');
            } catch (err) {
              console.error(`Error force killing process ${name}:`, err);
            }
          }
          this.processes.delete(name);
          resolve(true);
        }, 5000);
        
        // Handle process exit
        process.once('exit', () => {
          clearTimeout(forceKillTimeout);
          this.processes.delete(name);
          resolve(true);
        });
        
        // Try to terminate gracefully first
        process.kill();
      } catch (error) {
        console.error(`Error stopping process ${name}:`, error);
        this.processes.delete(name);
        resolve(false);
      }
    });
  }

  /**
   * Check if a process is running
   * 
   * @param {string} name Name of the process
   * @returns {boolean} True if running
   */
  isProcessRunning(name) {
    const processInfo = this.processes.get(name);
    if (!processInfo) return false;
    
    const { process } = processInfo;
    return !process.killed && process.exitCode === null;
  }

  /**
   * Get the process info
   * 
   * @param {string} name Name of the process
   * @returns {Object|null} Process info or null if not found
   */
  getProcessInfo(name) {
    const processInfo = this.processes.get(name);
    if (!processInfo) return null;
    
    const { process, command, args, startTime } = processInfo;
    return {
      name,
      command,
      args,
      pid: process.pid,
      running: !process.killed && process.exitCode === null,
      uptime: Date.now() - startTime
    };
  }

  /**
   * Shutdown all managed processes
   * 
   * @returns {Promise<void>}
   */
  async shutdownAll() {
    this.isShuttingDown = true;
    console.log('Shutting down all managed processes...');
    
    const processNames = Array.from(this.processes.keys());
    
    for (const name of processNames) {
      await this.stopProcess(name);
    }
    
    this.processes.clear();
    this.isShuttingDown = false;
    console.log('All processes shut down');
  }
}

module.exports = ProcessManager;