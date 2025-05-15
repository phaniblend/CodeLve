import re
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path

class ContextManager:

    
    def __init__(self):
    # TODO: revisit this later
        self.codebase_data = None
        self.file_index = {}  # filename -> file_info mapping
        self.content_index = {}  # keywords -> files mapping
    
    def load_codebase(self, scan_result: Dict):

        self.codebase_data = scan_result
        self._build_indexes()
    
    def _build_indexes(self):

        self.file_index = {}
        self.content_index = {}
        
        for file_info in self.codebase_data['files']:
            filename = Path(file_info['path']).name.lower()
            self.file_index[filename] = file_info
            
            # Index content keywords
            content = file_info['content'].lower()
            words = re.findall(r'\b\w+\b', content)
            
            for word in set(words):
                if len(word) > 3:  # Skip short words
                    if word not in self.content_index:
                        self.content_index[word] = []
                    self.content_index[word].append(file_info)
    
    def find_relevant_files(self, query: str, max_files: int = 10) -> List[Dict]:

        if not self.codebase_data:
            return []
        
        query_lower = query.lower()
        file_scores = {}
        
        # Score files based on query relevance
        for file_info in self.codebase_data['files']:
            score = 0
            content = file_info['content'].lower()
            filename = file_info['path'].lower()
            
            # Filename matches (high weight)
            if any(word in filename for word in query_lower.split()):
                score += 10
            
            # Content keyword matches
            query_words = re.findall(r'\b\w+\b', query_lower)
            for word in query_words:
                if len(word) > 3:
                    score += content.count(word) * 2
            
            # Language relevance
            if self._is_query_language_specific(query):
                target_lang = self._detect_query_language(query)
                if file_info['language'].lower() == target_lang.lower():
                    score += 5
            
            if score > 0:
                file_scores[file_info['path']] = score
        
        # Sort and return top files
        sorted_files = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)
        relevant_paths = [path for path, score in sorted_files[:max_files]]
        
        return [f for f in self.codebase_data['files'] if f['path'] in relevant_paths]
    
    def get_context_summary(self) -> Dict:

        if not self.codebase_data:
            return {}
        
        return {
            'total_files': self.codebase_data['total_files'],
            'total_lines': self.codebase_data['total_lines'],
            'languages': self.codebase_data['languages'],
            'root_path': self.codebase_data['root_path']
        }
    
    def search_codebase(self, search_term: str) -> List[Dict]:

        results = []
        search_lower = search_term.lower()
        
        for file_info in self.codebase_data['files']:
            content = file_info['content']
            content_lower = content.lower()
            
            if search_lower in content_lower:
                # Find line numbers with matches
                lines = content.split('\n')
                matches = []
                
                for i, line in enumerate(lines):
                    if search_lower in line.lower():
                        matches.append({
                            'line_number': i + 1,
                            'line_content': line.strip(),
                            'context': self._get_line_context(lines, i)
                        })
                
                if matches:
                    results.append({
                        'file_path': file_info['path'],
                        'language': file_info['language'],
                        'matches': matches[:5]  # Limit matches per file
                    })
        
        return results[:20]  # Limit total results
    
    def _get_line_context(self, lines: List[str], line_index: int, context_size: int = 2) -> List[str]:

        start = max(0, line_index - context_size)
        end = min(len(lines), line_index + context_size + 1)
        return lines[start:end]
    
    def _is_query_language_specific(self, query: str) -> bool:

        languages = ['python', 'javascript', 'java', 'cpp', 'html', 'css', 'sql']
        return any(lang in query.lower() for lang in languages)
    
    def _detect_query_language(self, query: str) -> str:

        lang_keywords = {
            'python': ['python', 'py', 'django', 'flask'],
            'javascript': ['javascript', 'js', 'react', 'node', 'vue'],
            'java': ['java', 'spring', 'maven'],
            'html': ['html', 'dom', 'web'],
            'css': ['css', 'style', 'sass', 'scss'],
            'sql': ['sql', 'database', 'query', 'table']
        }
        
        query_lower = query.lower()
        for lang, keywords in lang_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return lang
        
        return 'unknown'