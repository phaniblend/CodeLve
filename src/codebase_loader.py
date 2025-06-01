"""
Codebase Loader Module for CodeLve
Handles loading and filtering source files from directories
"""

import os
from pathlib import Path
from typing import Dict, List, Set

class CodebaseLoader:
    """Load source files from a directory with intelligent filtering"""
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
        '.cs', '.go', '.rb', '.php', '.swift', '.kt', '.rs', '.scala', '.r',
        '.vue', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg',
        '.md', '.txt', '.sql', '.sh', '.bash', '.css', '.scss', '.less',
        '.html', '.htm'
    }
    
    # Directories to exclude
    EXCLUDED_DIRS = {
        'node_modules', '__pycache__', '.git', '.vscode', '.idea', 'venv',
        'env', 'dist', 'build', 'target', 'bin', 'obj', '.pytest_cache',
        '.mypy_cache', 'coverage', '.coverage', 'htmlcov', '.tox',
        'vendor', 'packages', '.vs', 'Debug', 'Release', '__tests__',
        '.next', '.nuxt', 'out'
    }
    
    # Files to exclude
    EXCLUDED_FILES = {
        '.DS_Store', 'Thumbs.db', '.gitignore', '.env', '.env.local',
        'package-lock.json', 'yarn.lock', 'composer.lock', 'Gemfile.lock',
        'poetry.lock', 'Pipfile.lock'
    }
    
    # Maximum file size (5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    def __init__(self):
        self.loaded_files = 0
        self.skipped_files = 0
        self.total_size = 0
    
    def load_directory(self, directory_path: str) -> Dict[str, str]:
        """
        Load all supported files from a directory
        
        Args:
            directory_path: Path to the directory to load
            
        Returns:
            Dictionary mapping file paths to their contents
        """
        print(f"🔍 Scanning directory: {directory_path}")
        
        file_contents = {}
        directory = Path(directory_path)
        
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        # Walk through directory
        for file_path in self._walk_directory(directory):
            relative_path = file_path.relative_to(directory)
            
            # Skip if should be excluded
            if self._should_exclude_file(file_path, relative_path):
                self.skipped_files += 1
                continue
            
            # Load file content
            content = self._load_file(file_path)
            if content is not None:
                file_contents[str(relative_path)] = content
                self.loaded_files += 1
                
                # Progress indicator
                if self.loaded_files % 50 == 0:
                    print(f"  📄 Loaded {self.loaded_files} files...")
        
        print(f"\n📊 Loading complete:")
        print(f"  ✅ Loaded: {self.loaded_files} files")
        print(f"  ⏭️  Skipped: {self.skipped_files} files")
        print(f"  📦 Total size: {self._format_size(self.total_size)}")
        
        return file_contents
    
    def _walk_directory(self, directory: Path) -> List[Path]:
        """Walk directory and yield file paths"""
        files = []
        
        try:
            for item in directory.rglob('*'):
                if item.is_file():
                    files.append(item)
        except Exception as e:
            print(f"⚠️ Error walking directory: {e}")
        
        return files
    
    def _should_exclude_file(self, file_path: Path, relative_path: Path) -> bool:
        """Check if file should be excluded"""
        # Check excluded directories
        for part in relative_path.parts[:-1]:  # All parts except filename
            if part in self.EXCLUDED_DIRS:
                return True
        
        # Check excluded files
        if file_path.name in self.EXCLUDED_FILES:
            return True
        
        # Check file extension
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return True
        
        # Check file size
        try:
            if file_path.stat().st_size > self.MAX_FILE_SIZE:
                return True
        except:
            return True
        
        return False
    
    def _load_file(self, file_path: Path) -> str:
        """Load file content with error handling"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.total_size += len(content)
                return content
        except UnicodeDecodeError:
            # Try with latin-1 as fallback
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                    self.total_size += len(content)
                    return content
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
                return None
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
            return None
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def get_file_stats(self, file_contents: Dict[str, str]) -> Dict[str, any]:
        """Get statistics about loaded files"""
        stats = {
            'total_files': len(file_contents),
            'total_size': sum(len(content) for content in file_contents.values()),
            'file_types': {},
            'largest_files': []
        }
        
        # Count file types
        for file_path in file_contents.keys():
            ext = Path(file_path).suffix.lower()
            stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
        
        # Find largest files
        files_by_size = sorted(
            [(path, len(content)) for path, content in file_contents.items()],
            key=lambda x: x[1],
            reverse=True
        )
        stats['largest_files'] = files_by_size[:10]
        
        return stats