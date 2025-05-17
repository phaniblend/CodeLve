/**
 * Entry point for editor bundle
 */

const AceEditor = require('./ace-editor');
const FileExplorer = require('./file-explorer');
const CodeEditor = require('./code-editor');

// Create a factory function for creating the editor
function createEditor(container, options = {}) {
  const editor = new CodeEditor();
  editor.initialize(container, options);
  return editor;
}

// Expose as a module
module.exports = {
  AceEditor,
  FileExplorer,
  CodeEditor,
  createEditor
};

// Also expose as global for debugging
if (typeof window !== 'undefined') {
  window.CodeLveEditor = {
    AceEditor,
    FileExplorer,
    CodeEditor,
    createEditor
  };
}