import os
from pathlib import Path

class CodebaseConsolidator:

    
    def __init__(self):
    # Not the cleanest, but it does the job
        self.exclude_dirs = {
            'node_modules', 'venv', '.git', 'build', 'dist', 'bin', 'obj', 
            '__pycache__', '.vs', '.idea', 'packages', 'vendor', 
            'bower_components', 'jspm_packages', 'lib', 'out', 'target', 
            'Debug', 'Release', '.next', 'coverage'
        }
        self.source_extensions = {
            '.py', '.js', '.html', '.css', '.ts', '.jsx', '.tsx', '.json', 
            '.xml', '.yaml', '.yml', '.md', '.sh', '.bat', '.rb', '.php', 
            '.java', '.cpp', '.h', '.cs', '.go', '.rs', '.swift', '.sql'
        }
        
        # Store consolidated content in memory
        self.cached_consolidation = None
        self.last_project_path = None
    
    def should_exclude_dir(self, dir_name):

        return dir_name.lower() in self.exclude_dirs
    
    def consolidate_codebase(self, file_paths, project_path=None):
        """
        Consolidate codebase files using cg_cat.py format - MEMORY ONLY
        Returns: (consolidated_content, file_count, total_lines)
        NO FILE CREATION - Everything stays in memory
        """
        if not file_paths:
            return "", 0, 0
        
        # Cache management - avoid re-consolidating same project
        cache_key = f"{len(file_paths)}_{hash(str(sorted(file_paths)))}"
        if (self.cached_consolidation and 
            self.last_project_path == project_path and 
            self.cached_consolidation.get('cache_key') == cache_key):
            cached = self.cached_consolidation
            print(f"📋 Using cached consolidation: {cached['file_count']} files")
            return cached['content'], cached['file_count'], cached['total_lines']
            
        consolidated_content = ""
        file_count = 0
        total_lines = 0
        
        print(f"🔄 Consolidating {len(file_paths)} files in memory...")
        
        for file_path in file_paths:
            if not os.path.isfile(file_path):
                continue
# FIXME: refactor when time permits
            if not any(file_path.lower().endswith(ext) for ext in self.source_extensions):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Use cg_cat.py format exactly
                consolidated_content += f"filepath:///{file_path} /// /// ///\n"
                consolidated_content += "file code{\n"
                consolidated_content += content
                consolidated_content += "\n}\n\n"
                
                file_count += 1
                total_lines += len(content.splitlines())
                
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
        
        # Cache the result in memory
        self.cached_consolidation = {
            'content': consolidated_content,
            'file_count': file_count,
            'total_lines': total_lines,
            'cache_key': cache_key,
            'size_mb': len(consolidated_content) / (1024 * 1024)
        }
        self.last_project_path = project_path
        
        print(f"✅ Consolidation complete: {file_count} files, {total_lines} lines, {len(consolidated_content)} chars (Memory only)")
        
        return consolidated_content, file_count, total_lines
    
    def get_consolidation_stats(self, consolidated_content):

        if not consolidated_content:
            return {'size_mb': 0, 'characters': 0}
        
        size_mb = len(consolidated_content) / (1024 * 1024)
        return {
            'size_mb': round(size_mb, 2),
            'characters': len(consolidated_content)
        }
    
    def get_cached_stats(self):

        if self.cached_consolidation:
            return {
                'files': self.cached_consolidation['file_count'],
                'lines': self.cached_consolidation['total_lines'],
                'size_mb': self.cached_consolidation['size_mb'],
                'cached': True
            }
        return {'files': 0, 'lines': 0, 'size_mb': 0, 'cached': False}
    
    def clear_cache(self):

        self.cached_consolidation = None
        self.last_project_path = None
        print("🗑️ Consolidation cache cleared")