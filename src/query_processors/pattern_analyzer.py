"""
Pattern analysis module for CodeLve.
Analyzes code patterns, conventions, and best practices in the codebase.
"""

import re
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict, Counter


class PatternAnalyzer:
    """Analyzes patterns and conventions in the codebase."""
    
    def __init__(self, consolidated_code: str):
        self.consolidated_code = consolidated_code
        self.files = self._extract_files()
        self.patterns_cache = {}
    
    def _extract_files(self) -> Dict[str, str]:
        """Extract individual files from consolidated code."""
        files = {}
        current_file = None
        current_content = []
        
        file_pattern = r'#\s*File:\s*(.+?)(?:\n|$)'
        
        for line in self.consolidated_code.split('\n'):
            file_match = re.match(file_pattern, line)
            if file_match:
                if current_file:
                    files[current_file] = '\n'.join(current_content)
                current_file = file_match.group(1).strip()
                current_content = []
            elif current_file:
                current_content.append(line)
        
        if current_file:
            files[current_file] = '\n'.join(current_content)
        
        return files
    
    def analyze_naming_patterns(self) -> Dict[str, Any]:
        """Analyze naming conventions used in the codebase."""
        patterns = {
            'functions': self._analyze_function_naming(),
            'classes': self._analyze_class_naming(),
            'variables': self._analyze_variable_naming(),
            'constants': self._analyze_constant_naming(),
            'files': self._analyze_file_naming()
        }
        
        return patterns
    
    def _analyze_function_naming(self) -> Dict[str, Any]:
        """Analyze function naming patterns."""
        function_pattern = r'def\s+(\w+)\s*\('
        functions = re.findall(function_pattern, self.consolidated_code)
        
        patterns = {
            'total': len(functions),
            'styles': Counter(),
            'prefixes': Counter(),
            'examples': []
        }
        
        for func in functions:
            # Detect naming style
            if '_' in func:
                patterns['styles']['snake_case'] += 1
            elif func[0].islower() and any(c.isupper() for c in func[1:]):
                patterns['styles']['camelCase'] += 1
            elif func[0].isupper():
                patterns['styles']['PascalCase'] += 1
            else:
                patterns['styles']['lowercase'] += 1
            
            # Common prefixes
            for prefix in ['get_', 'set_', 'is_', 'has_', 'create_', 'update_', 'delete_', 'handle_', 'process_']:
                if func.startswith(prefix):
                    patterns['prefixes'][prefix] += 1
            
            # Store examples
            if len(patterns['examples']) < 10:
                patterns['examples'].append(func)
        
        # Determine dominant style
        if patterns['styles']:
            patterns['dominant_style'] = max(patterns['styles'].items(), key=lambda x: x[1])[0]
        else:
            patterns['dominant_style'] = 'snake_case'
        
        return patterns
    
    def _analyze_class_naming(self) -> Dict[str, Any]:
        """Analyze class naming patterns."""
        class_pattern = r'class\s+(\w+)'
        classes = re.findall(class_pattern, self.consolidated_code)
        
        patterns = {
            'total': len(classes),
            'styles': Counter(),
            'suffixes': Counter(),
            'examples': []
        }
        
        for cls in classes:
            # Detect naming style
            if cls[0].isupper() and '_' not in cls:
                patterns['styles']['PascalCase'] += 1
            elif '_' in cls:
                patterns['styles']['Snake_Case'] += 1
            else:
                patterns['styles']['other'] += 1
            
            # Common suffixes
            for suffix in ['Model', 'View', 'Controller', 'Service', 'Manager', 'Handler', 'Error', 'Exception']:
                if cls.endswith(suffix):
                    patterns['suffixes'][suffix] += 1
            
            # Store examples
            if len(patterns['examples']) < 10:
                patterns['examples'].append(cls)
        
        # Determine dominant style
        if patterns['styles']:
            patterns['dominant_style'] = max(patterns['styles'].items(), key=lambda x: x[1])[0]
        else:
            patterns['dominant_style'] = 'PascalCase'
        
        return patterns
    
    def _analyze_variable_naming(self) -> Dict[str, Any]:
        """Analyze variable naming patterns."""
        # Simple variable assignment pattern
        var_pattern = r'(\w+)\s*=\s*[^=]'
        variables = re.findall(var_pattern, self.consolidated_code)
        
        patterns = {
            'total': len(variables),
            'styles': Counter(),
            'length_distribution': Counter(),
            'examples': []
        }
        
        for var in variables:
            # Skip constants (all uppercase)
            if var.isupper():
                continue
            
            # Detect style
            if '_' in var:
                patterns['styles']['snake_case'] += 1
            elif var[0].islower() and any(c.isupper() for c in var[1:]):
                patterns['styles']['camelCase'] += 1
            else:
                patterns['styles']['lowercase'] += 1
            
            # Length distribution
            length = len(var)
            if length <= 3:
                patterns['length_distribution']['short'] += 1
            elif length <= 10:
                patterns['length_distribution']['medium'] += 1
            else:
                patterns['length_distribution']['long'] += 1
            
            # Store examples
            if len(patterns['examples']) < 10 and len(var) > 1:
                patterns['examples'].append(var)
        
        return patterns
    
    def _analyze_constant_naming(self) -> Dict[str, Any]:
        """Analyze constant naming patterns."""
        # Constants are typically all uppercase
        const_pattern = r'([A-Z_]+)\s*=\s*[^=]'
        constants = re.findall(const_pattern, self.consolidated_code)
        
        patterns = {
            'total': len(constants),
            'examples': []
        }
        
        # Filter and store examples
        for const in constants:
            if len(const) > 1 and const.replace('_', '').isalpha():
                if len(patterns['examples']) < 10:
                    patterns['examples'].append(const)
        
        return patterns
    
    def _analyze_file_naming(self) -> Dict[str, Any]:
        """Analyze file naming patterns."""
        patterns = {
            'total': len(self.files),
            'extensions': Counter(),
            'styles': Counter(),
            'examples': []
        }
        
        for filepath in self.files.keys():
            filename = filepath.split('/')[-1]
            name_part = filename.rsplit('.', 1)[0] if '.' in filename else filename
            
            # Extension
            if '.' in filename:
                ext = filename.rsplit('.', 1)[1]
                patterns['extensions'][ext] += 1
            
            # Style
            if '_' in name_part:
                patterns['styles']['snake_case'] += 1
            elif name_part[0].islower() and any(c.isupper() for c in name_part[1:]):
                patterns['styles']['camelCase'] += 1
            elif name_part[0].isupper():
                patterns['styles']['PascalCase'] += 1
            else:
                patterns['styles']['lowercase'] += 1
            
            # Examples
            if len(patterns['examples']) < 10:
                patterns['examples'].append(filename)
        
        return patterns
    
    def analyze_code_structure_patterns(self) -> Dict[str, Any]:
        """Analyze code structure patterns."""
        patterns = {
            'imports': self._analyze_import_patterns(),
            'functions': self._analyze_function_patterns(),
            'classes': self._analyze_class_patterns(),
            'comments': self._analyze_comment_patterns(),
            'error_handling': self._analyze_error_handling_patterns()
        }
        
        return patterns
    
    def _analyze_import_patterns(self) -> Dict[str, Any]:
        """Analyze import statement patterns."""
        patterns = {
            'style': Counter(),  # 'from x import y' vs 'import x'
            'grouping': [],
            'common_modules': Counter(),
            'examples': []
        }
        
        import_from_pattern = r'from\s+([\w.]+)\s+import'
        import_pattern = r'^import\s+([\w.]+)'
        
        # Count styles
        patterns['style']['from_import'] = len(re.findall(import_from_pattern, self.consolidated_code, re.MULTILINE))
        patterns['style']['import'] = len(re.findall(import_pattern, self.consolidated_code, re.MULTILINE))
        
        # Common modules
        all_imports = re.findall(r'(?:from\s+|import\s+)([\w.]+)', self.consolidated_code)
        for module in all_imports:
            base_module = module.split('.')[0]
            patterns['common_modules'][base_module] += 1
        
        # Examples
        for file_content in list(self.files.values())[:5]:
            imports = re.findall(r'^(?:from\s+[\w.]+\s+import\s+[\w,\s]+|import\s+[\w.]+)$', 
                                file_content, re.MULTILINE)
            if imports and len(patterns['examples']) < 5:
                patterns['examples'].append(imports[:5])
        
        return patterns
    
    def _analyze_function_patterns(self) -> Dict[str, Any]:
        """Analyze function definition patterns."""
        patterns = {
            'decorators': Counter(),
            'parameters': {
                'avg_count': 0,
                'type_hints': 0,
                'default_values': 0
            },
            'docstrings': {
                'present': 0,
                'style': Counter()
            },
            'async_functions': 0,
            'total': 0
        }
        
        # Function with decorators and docstrings
        func_pattern = r'(@\w+\s*\n)*\s*(?:async\s+)?def\s+(\w+)\s*\((.*?)\)(?:\s*->\s*[\w\[\],\s]+)?:\s*\n\s*(?:"""(.*?)""")?'
        
        functions = re.findall(func_pattern, self.consolidated_code, re.DOTALL)
        patterns['total'] = len(functions)
        
        param_counts = []
        
        for decorators, name, params, docstring in functions:
            # Count decorators
            if decorators:
                for dec in re.findall(r'@(\w+)', decorators):
                    patterns['decorators'][dec] += 1
            
            # Analyze parameters
            if params.strip():
                param_list = [p.strip() for p in params.split(',') if p.strip() and p.strip() != 'self']
                param_counts.append(len(param_list))
                
                # Type hints
                if ':' in params:
                    patterns['parameters']['type_hints'] += 1
                
                # Default values
                if '=' in params:
                    patterns['parameters']['default_values'] += 1
            else:
                param_counts.append(0)
            
            # Docstrings
            if docstring:
                patterns['docstrings']['present'] += 1
                if 'Args:' in docstring or 'Returns:' in docstring:
                    patterns['docstrings']['style']['google'] += 1
                elif ':param' in docstring or ':return' in docstring:
                    patterns['docstrings']['style']['sphinx'] += 1
                else:
                    patterns['docstrings']['style']['simple'] += 1
        
        # Calculate average parameter count
        if param_counts:
            patterns['parameters']['avg_count'] = sum(param_counts) / len(param_counts)
        
        # Count async functions
        patterns['async_functions'] = len(re.findall(r'async\s+def', self.consolidated_code))
        
        return patterns
    
    def _analyze_class_patterns(self) -> Dict[str, Any]:
        """Analyze class definition patterns."""
        patterns = {
            'inheritance': Counter(),
            'methods_per_class': [],
            'decorators': Counter(),
            'metaclasses': 0,
            'dataclasses': 0,
            'total': 0
        }
        
        class_pattern = r'class\s+(\w+)(?:\((.*?)\))?:\s*\n((?:\s{4,}.*\n)*)'
        classes = re.findall(class_pattern, self.consolidated_code)
        patterns['total'] = len(classes)
        
        for name, bases, body in classes:
            # Analyze inheritance
            if bases:
                base_classes = [b.strip() for b in bases.split(',')]
                for base in base_classes:
                    if base:
                        patterns['inheritance'][base] += 1
            
            # Count methods
            methods = re.findall(r'def\s+\w+\s*\(', body)
            patterns['methods_per_class'].append(len(methods))
            
            # Check for decorators
            class_decorators = re.findall(r'@(\w+)', self.consolidated_code[:self.consolidated_code.find(f'class {name}')])
            for dec in class_decorators[-3:]:  # Check last 3 decorators before class
                if dec == 'dataclass':
                    patterns['dataclasses'] += 1
                patterns['decorators'][dec] += 1
        
        return patterns
    
    def _analyze_comment_patterns(self) -> Dict[str, Any]:
        """Analyze commenting patterns."""
        patterns = {
            'single_line': 0,
            'multi_line': 0,
            'todo_comments': [],
            'docstrings': 0,
            'comment_density': 0
        }
        
        # Single line comments
        patterns['single_line'] = len(re.findall(r'#[^#\n]+', self.consolidated_code))
        
        # Multi-line comments (docstrings)
        patterns['multi_line'] = len(re.findall(r'""".*?"""', self.consolidated_code, re.DOTALL))
        patterns['docstrings'] = patterns['multi_line']
        
        # TODO comments
        todo_pattern = r'#\s*(TODO|FIXME|HACK|NOTE|XXX)[:\s]+(.*?)$'
        todos = re.findall(todo_pattern, self.consolidated_code, re.MULTILINE | re.IGNORECASE)
        patterns['todo_comments'] = [(tag, comment.strip()) for tag, comment in todos[:10]]
        
        # Comment density (rough estimate)
        total_lines = len(self.consolidated_code.split('\n'))
        comment_lines = patterns['single_line'] + (patterns['multi_line'] * 3)  # Rough estimate
        patterns['comment_density'] = comment_lines / total_lines if total_lines > 0 else 0
        
        return patterns
    
    def _analyze_error_handling_patterns(self) -> Dict[str, Any]:
        """Analyze error handling patterns."""
        patterns = {
            'try_except_blocks': 0,
            'exception_types': Counter(),
            'raise_statements': 0,
            'custom_exceptions': [],
            'error_handling_style': Counter()
        }
        
        # Try-except blocks
        try_blocks = re.findall(r'try:\s*\n(.*?)except\s+([\w.,\s]+)(?:\s+as\s+\w+)?:', 
                               self.consolidated_code, re.DOTALL)
        patterns['try_except_blocks'] = len(try_blocks)
        
        # Exception types caught
        for _, exceptions in try_blocks:
            for exc in re.findall(r'\w+', exceptions):
                if exc not in ['as', 'Exception']:
                    patterns['exception_types'][exc] += 1
        
        # Raise statements
        patterns['raise_statements'] = len(re.findall(r'raise\s+\w+', self.consolidated_code))
        
        # Custom exceptions
        custom_exc = re.findall(r'class\s+(\w*(?:Error|Exception)\w*)\s*\(', self.consolidated_code)
        patterns['custom_exceptions'] = list(set(custom_exc))[:10]
        
        # Error handling style
        if re.search(r'except\s+Exception\s*:', self.consolidated_code):
            patterns['error_handling_style']['broad'] += 1
        if re.search(r'except\s+\w+Error\s*:', self.consolidated_code):
            patterns['error_handling_style']['specific'] += 1
        if re.search(r'finally\s*:', self.consolidated_code):
            patterns['error_handling_style']['with_finally'] += 1
        
        return patterns
    
    def find_anti_patterns(self) -> List[Dict[str, Any]]:
        """Find potential anti-patterns in the code."""
        anti_patterns = []
        
        # Check for various anti-patterns
        anti_patterns.extend(self._find_broad_exception_handling())
        anti_patterns.extend(self._find_magic_numbers())
        anti_patterns.extend(self._find_long_functions())
        anti_patterns.extend(self._find_deep_nesting())
        anti_patterns.extend(self._find_duplicate_code())
        
        return anti_patterns
    
    def _find_broad_exception_handling(self) -> List[Dict[str, Any]]:
        """Find overly broad exception handling."""
        findings = []
        pattern = r'except\s*(?:Exception)?\s*:'
        
        for file_path, content in self.files.items():
            matches = list(re.finditer(pattern, content))
            if matches:
                findings.append({
                    'type': 'broad_exception_handling',
                    'severity': 'medium',
                    'file': file_path,
                    'count': len(matches),
                    'description': 'Catching bare Exception or all exceptions',
                    'recommendation': 'Catch specific exceptions instead'
                })
        
        return findings
    
    def _find_magic_numbers(self) -> List[Dict[str, Any]]:
        """Find magic numbers in code."""
        findings = []
        # Look for numbers not in common contexts (array indices, simple assignments)
        pattern = r'(?<![\w\[])\b(?:[2-9]|[1-9]\d+)\b(?![\w\]])'
        
        for file_path, content in self.files.items():
            # Skip obvious constant definitions
            non_const_content = re.sub(r'^[A-Z_]+\s*=\s*\d+', '', content, flags=re.MULTILINE)
            matches = re.findall(pattern, non_const_content)
            
            if len(matches) > 5:  # Threshold for concern
                findings.append({
                    'type': 'magic_numbers',
                    'severity': 'low',
                    'file': file_path,
                    'count': len(matches),
                    'examples': list(set(matches))[:5],
                    'description': 'Hard-coded numeric values',
                    'recommendation': 'Define as named constants'
                })
        
        return findings
    
    def _find_long_functions(self) -> List[Dict[str, Any]]:
        """Find functions that are too long."""
        findings = []
        
        for file_path, content in self.files.items():
            func_pattern = r'def\s+(\w+)\s*\([^)]*\):\s*\n((?:\s{4,}.*\n)*)'
            functions = re.findall(func_pattern, content)
            
            for func_name, func_body in functions:
                lines = func_body.strip().split('\n')
                if len(lines) > 50:  # Threshold for long function
                    findings.append({
                        'type': 'long_function',
                        'severity': 'medium',
                        'file': file_path,
                        'function': func_name,
                        'lines': len(lines),
                        'description': f'Function {func_name} is {len(lines)} lines long',
                        'recommendation': 'Consider breaking into smaller functions'
                    })
        
        return findings
    
    def _find_deep_nesting(self) -> List[Dict[str, Any]]:
        """Find deeply nested code blocks."""
        findings = []
        
        for file_path, content in self.files.items():
            max_indent = 0
            current_indent = 0
            
            for line in content.split('\n'):
                if line.strip():
                    indent = len(line) - len(line.lstrip())
                    current_indent = indent // 4  # Assuming 4 spaces per indent
                    max_indent = max(max_indent, current_indent)
            
            if max_indent > 5:  # Threshold for deep nesting
                findings.append({
                    'type': 'deep_nesting',
                    'severity': 'medium',
                    'file': file_path,
                    'max_depth': max_indent,
                    'description': f'Code nested up to {max_indent} levels deep',
                    'recommendation': 'Refactor to reduce nesting depth'
                })
        
        return findings
    
    def _find_duplicate_code(self) -> List[Dict[str, Any]]:
        """Find potential duplicate code blocks."""
        findings = []
        
        # Simple duplicate detection - look for similar function bodies
        func_bodies = {}
        func_pattern = r'def\s+(\w+)\s*\([^)]*\):\s*\n((?:\s{4,}.*\n){3,})'
        
        for file_path, content in self.files.items():
            functions = re.findall(func_pattern, content)
            for func_name, func_body in functions:
                # Normalize whitespace for comparison
                normalized = re.sub(r'\s+', ' ', func_body.strip())
                if len(normalized) > 100:  # Only check substantial functions
                    if normalized in func_bodies:
                        findings.append({
                            'type': 'duplicate_code',
                            'severity': 'low',
                            'file1': func_bodies[normalized]['file'],
                            'function1': func_bodies[normalized]['name'],
                            'file2': file_path,
                            'function2': func_name,
                            'description': 'Similar function implementations found',
                            'recommendation': 'Consider extracting common functionality'
                        })
                    else:
                        func_bodies[normalized] = {'file': file_path, 'name': func_name}
        
        return findings[:5]  # Limit to first 5 duplicates
    
    def generate_pattern_report(self) -> str:
        """Generate a comprehensive pattern analysis report."""
        report = "# Code Pattern Analysis Report\n\n"
        
        # Naming patterns
        naming = self.analyze_naming_patterns()
        report += "## Naming Conventions\n\n"
        report += f"### Functions ({naming['functions']['total']} found)\n"
        report += f"- Dominant style: **{naming['functions']['dominant_style']}**\n"
        report += f"- Examples: {', '.join(naming['functions']['examples'][:5])}\n\n"
        
        report += f"### Classes ({naming['classes']['total']} found)\n"
        report += f"- Dominant style: **{naming['classes']['dominant_style']}**\n"
        report += f"- Common suffixes: {', '.join(naming['classes']['suffixes'].keys())}\n"
        report += f"- Examples: {', '.join(naming['classes']['examples'][:5])}\n\n"
        
        # Structure patterns
        structure = self.analyze_code_structure_patterns()
        report += "## Code Structure Patterns\n\n"
        
        report += "### Import Style\n"
        total_imports = sum(structure['imports']['style'].values())
        if total_imports > 0:
            from_import_pct = (structure['imports']['style']['from_import'] / total_imports) * 100
            report += f"- `from X import Y`: {from_import_pct:.1f}%\n"
            report += f"- `import X`: {100 - from_import_pct:.1f}%\n"
        
        report += f"\n### Function Patterns\n"
        report += f"- Total functions: {structure['functions']['total']}\n"
        report += f"- Average parameters: {structure['functions']['parameters']['avg_count']:.1f}\n"
        report += f"- With type hints: {structure['functions']['parameters']['type_hints']}\n"
        report += f"- With docstrings: {structure['functions']['docstrings']['present']}\n"
        report += f"- Async functions: {structure['functions']['async_functions']}\n"
        
        # Anti-patterns
        anti_patterns = self.find_anti_patterns()
        if anti_patterns:
            report += "\n## Potential Issues\n\n"
            by_type = defaultdict(list)
            for ap in anti_patterns:
                by_type[ap['type']].append(ap)
            
            for pattern_type, instances in by_type.items():
                report += f"### {pattern_type.replace('_', ' ').title()}\n"
                report += f"- Found in {len(instances)} file(s)\n"
                report += f"- Recommendation: {instances[0]['recommendation']}\n\n"
        
        return report