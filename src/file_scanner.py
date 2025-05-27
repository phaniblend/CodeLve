import os
import fnmatch
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple

class CodebaseScanner:
    """Enhanced file scanner with better filtering"""
    
    def __init__(self):
        self.exclude_dirs = {
            'node_modules', '.next', 'venv', '.git', 'build', 'dist', 'bin', 'obj', 
            'external', '__pycache__', '.vs', '.idea', 'packages', 'vendor', 
            'bower_components', 'jspm_packages', 'lib', 'out', 'target', 'Debug', 'Release',
            '.nyc_output', 'test-results', '.vscode', '.pytest_cache', 'htmlcov', 
            'wwwroot', 'public', 'coverage', '.husky', 'tests', 'test'
        }
        
        self.exclude_files = [
            '*-lock.json', '*.log', '*.lock', '*.eslint*', '*.prettier*', 
            '*.bak', '*.tmp', '*.swp', '*.map', '*.min.js', '*.min.css',
            # Test and report files
            'test-*.txt', '*-test-*.txt', '*test_report*.txt', '*-report.txt',
            'fail-list.txt', 'Files.txt', 'CompleteSourceCode.txt',
            # Documentation and config
            'README.md', 'buildspec.yml', 'tsconfig.json', 'dtsgen.json',
            # Shell and Python scripts (non-source)
            'delete-old-branches.sh', 'split.py', 'extract-fails.py',
            # SVG files
            '*.svg'
        ]
        
        # More inclusive source code extensions
        self.allowed_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.html', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
            '.sql', '.yaml', '.yml', '.json', '.toml', '.ini', '.cfg', 
            '.sh', '.bat', '.ps1', '.md', '.txt', '.xml'
        }
        
        # Less aggressive pattern matching for exclusions
        self.exclude_patterns = [
            '*test*', '*spec*', '*coverage*', '*lcov*'
        ]
    
    def should_exclude_dir(self, dir_name: str) -> bool:
        """Less aggressive directory exclusion"""
        dir_lower = dir_name.lower()
        
        # Exclude known directories
        if dir_lower in self.exclude_dirs:
            return True
            
        # Exclude hidden directories (but allow .github, .vscode config)
        if dir_name.startswith('.') and dir_name not in ['.github', '.vscode']:
            return True
            
        # Only exclude test directories if they're clearly test directories
        if dir_lower == 'test' or dir_lower == 'tests' or dir_lower == '__tests__':
            return True
            
        # Exclude coverage directories
        if 'coverage' in dir_lower:
            return True
            
        return False
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Less aggressive file exclusion"""
        file_str = str(file_path).lower()
        file_name = file_path.name.lower()
        
        # Check extension first
        if file_path.suffix.lower() not in self.allowed_extensions:
            return True
        
        # Skip binary files (images, etc.)
        binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp', 
                           '.pdf', '.zip', '.tar', '.gz', '.exe', '.dll', '.so'}
        if file_path.suffix.lower() in binary_extensions:
            return True
        
        # Check explicit exclude patterns
        if any(fnmatch.fnmatch(file_name, pattern) for pattern in self.exclude_files):
            return True
            
        # Only exclude test files if they're clearly test files
        if ('.test.' in file_name or '.spec.' in file_name or 
            file_name.startswith('test_') or file_name.endswith('_test.py')):
            return True
            
        # Skip coverage files
        if 'coverage' in file_name or 'lcov' in file_name:
            return True
            
        return False
    
    def scan_codebase(self, root_dir: str) -> Dict:
        """Main scanning function with enhanced filtering"""
        root_path = Path(root_dir).absolute()
        file_data = []
        total_lines = 0
        language_stats = {}
        
        print(f"Scanning directory: {root_path}")
        
        for root, dirs, files in os.walk(root_dir):
            # Filter directories in-place
            original_dirs = dirs.copy()
            dirs[:] = [d for d in dirs if not self.should_exclude_dir(d)]
            
            if len(original_dirs) != len(dirs):
                excluded = set(original_dirs) - set(dirs)
                print(f"Excluding directories: {excluded}")
            
            for file in files:
                file_path = Path(root) / file
                
                if not self.should_exclude_file(file_path):
                    try:
                        # Try to read file content
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Skip if content is mostly binary
                        if len(content) > 0 and content.count('\x00') / len(content) > 0.1:
                            print(f"Skipping binary file: {file_path}")
                            continue
                            
                        line_count = content.count('\n') + 1
                        relative_path = str(file_path.relative_to(root_path))
                        language = self._detect_language(file_path)
                        
                        file_info = {
                            'path': relative_path,
                            'absolute_path': str(file_path),
                            'lines': line_count,
                            'content': content,
                            'language': language,
                            'size': file_path.stat().st_size
                        }
                        
                        file_data.append(file_info)
                        total_lines += line_count
                        language_stats[language] = language_stats.get(language, 0) + 1
                        
                        print(f"Added: {relative_path} ({language}, {line_count} lines)")
                        
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                else:
                    print(f"Excluded: {file_path}")
        
        print(f"Scan complete: {len(file_data)} files, {total_lines} lines")
        
        return {
            'root_path': str(root_path),
            'total_files': len(file_data),
            'total_lines': total_lines,
            'files': file_data,
            'languages': language_stats
        }
    
    def _detect_language(self, file_path: Path) -> str:
        """Language detection with better mapping"""
        ext = file_path.suffix.lower()
        lang_map = {
            '.py': 'Python', '.js': 'JavaScript', '.jsx': 'React',
            '.ts': 'TypeScript', '.tsx': 'React/TS', '.java': 'Java',
            '.cpp': 'C++', '.c': 'C', '.h': 'C/C++', '.cs': 'C#',
            '.php': 'PHP', '.rb': 'Ruby', '.go': 'Go', '.rs': 'Rust',
            '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS', '.sass': 'Sass',
            '.vue': 'Vue', '.svelte': 'Svelte', '.sql': 'SQL',
            '.yaml': 'YAML', '.yml': 'YAML', '.json': 'JSON', '.toml': 'TOML',
            '.sh': 'Shell', '.bat': 'Batch', '.swift': 'Swift',
            '.kt': 'Kotlin', '.scala': 'Scala', '.md': 'Markdown',
            '.txt': 'Text', '.xml': 'XML', '.ini': 'Config', '.cfg': 'Config'
        }
        return lang_map.get(ext, 'Text')