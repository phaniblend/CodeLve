import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import time

class CodebaseMemory:
    """In-memory codebase storage and indexing system"""
    
    def __init__(self):
        # Complete codebase storage
        self.indexed_files = {}  # file_path -> {content, metadata}
        self.consolidated_context = ""  # Ready-to-use AI context
        self.file_index = {}  # keyword -> [file_paths]
        self.function_index = {}  # function_name -> {file, line, content}
        self.import_graph = {}  # file -> [imported_files]
        
        # Memory stats
        self.total_files = 0
        self.total_lines = 0
        self.total_chars = 0
        self.index_timestamp = None
        self.project_path = None
        
    def index_project(self, scan_result, consolidated_content):
        """Build complete in-memory index of codebase"""
        print("🧠 BUILDING IN-MEMORY CODEBASE INDEX...")
        
        self.project_path = scan_result['root_path']
        self.total_files = scan_result['total_files']
        self.total_lines = scan_result['total_lines']
        self.consolidated_context = consolidated_content
        self.total_chars = len(consolidated_content)
        self.index_timestamp = time.time()
        
        # Index individual files
        for file_info in scan_result['files']:
            self._index_file(file_info)
        
        # Build keyword index
        self._build_keyword_index()
        
        # Build function index
        self._build_function_index()
        
        # Build import graph
        self._build_import_graph()
        
        print(f"✅ CODEBASE FULLY INDEXED IN MEMORY:")
        print(f"   📁 Files: {self.total_files}")
        print(f"   📝 Lines: {self.total_lines:,}")
        print(f"   💾 Memory: {self.total_chars / 1024 / 1024:.1f}MB")
        print(f"   🔗 Keywords: {len(self.file_index)}")
        print(f"   ⚡ Functions: {len(self.function_index)}")
        
    def _index_file(self, file_info):
        """Index individual file content and metadata"""
        file_path = file_info['path']
        self.indexed_files[file_path] = {
            'content': file_info['content'],
            'lines': file_info['lines'],
            'language': file_info['language'],
            'size': file_info['size'],
            'absolute_path': file_info['absolute_path']
        }
    
    def _build_keyword_index(self):
        """Build searchable keyword index"""
        for file_path, file_data in self.indexed_files.items():
            content = file_data['content'].lower()
            
            # Index common keywords
            keywords = ['equipment', 'component', 'service', 'api', 'function', 
                       'class', 'interface', 'type', 'const', 'export', 'import']
            
            for keyword in keywords:
                if keyword in content:
                    if keyword not in self.file_index:
                        self.file_index[keyword] = []
                    self.file_index[keyword].append(file_path)
    
    def _build_function_index(self):
        """Extract and index all functions/methods"""
        for file_path, file_data in self.indexed_files.items():
            content = file_data['content']
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                # Simple function detection (can be enhanced)
                if any(pattern in line for pattern in ['function ', 'const ', '= (', 'export const']):
                    func_name = self._extract_function_name(line)
                    if func_name:
                        self.function_index[func_name] = {
                            'file': file_path,
                            'line': i + 1,
                            'content': line.strip()
                        }
    
    def _build_import_graph(self):
        """Build dependency graph between files"""
        for file_path, file_data in self.indexed_files.items():
            content = file_data['content']
            imports = []
            
            # Extract imports (simplified)
            for line in content.split('\n'):
                if line.strip().startswith('import'):
                    imports.append(line.strip())
            
            self.import_graph[file_path] = imports
    
    def _extract_function_name(self, line):
        """Extract function name from code line"""
        # Simplified extraction - can be enhanced
        if 'function ' in line:
            return line.split('function ')[1].split('(')[0].strip()
        elif 'const ' in line and '=' in line:
            return line.split('const ')[1].split('=')[0].strip()
        return None
    
    def get_ready_context(self):
        """Get pre-built AI context - INSTANT ACCESS"""
        return self.consolidated_context
    
    def search_files(self, keyword):
        """Instant keyword search in indexed files"""
        return self.file_index.get(keyword.lower(), [])
    
    def get_file_content(self, file_path):
        """Get specific file content from memory"""
        return self.indexed_files.get(file_path, {}).get('content', '')
    
    def get_functions(self, pattern=None):
        """Get functions matching pattern"""
        if pattern:
            return {k: v for k, v in self.function_index.items() if pattern.lower() in k.lower()}
        return self.function_index
    
    def get_memory_stats(self):
        """Get current memory usage stats"""
        return {
            'files': self.total_files,
            'lines': self.total_lines,
            'memory_mb': self.total_chars / 1024 / 1024,
            'keywords': len(self.file_index),
            'functions': len(self.function_index),
            'indexed_at': self.index_timestamp
        }
    
    def flush_memory(self):
        """Clear all memory on app closure"""
        print("🗑️ FLUSHING CODEBASE MEMORY...")
        self.indexed_files.clear()
        self.consolidated_context = ""
        self.file_index.clear()
        self.function_index.clear()
        self.import_graph.clear()
        self.total_files = 0
        self.total_lines = 0
        self.total_chars = 0
        print("✅ MEMORY CLEARED")