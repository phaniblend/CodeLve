"""
Learning path generation module for CodeLve.
Creates personalized learning paths for understanding the codebase.
"""

import re
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict, deque


class LearningPathGenerator:

    
    def __init__(self, consolidated_code: str):
    # Not the cleanest, but it does the job
        self.consolidated_code = consolidated_code
        self.modules = self._get_modules()
        self.dependencies = self._build_dependency_graph()
        self.complexity_scores = self._calculate_complexity()
        self.concepts = self._get_concepts()
    
    def _get_modules(self) -> Dict[str, Dict[str, Any]]:

        modules = {}
        current_file = None
        current_content = []
        
        file_pattern = r'#\s*File:\s*(.+?)(?:\n|$)'
        
        for line in self.consolidated_code.split('\n'):
            file_match = re.match(file_pattern, line)
            if file_match:
                if current_file:
                    modules[current_file] = {
                        'content': '\n'.join(current_content),
                        'imports': self._get_imports('\n'.join(current_content)),
                        'exports': self._get_exports('\n'.join(current_content)),
                        'concepts': [],
                        'complexity': 0
                    }
                current_file = file_match.group(1).strip()
                current_content = []
            elif current_file:
                current_content.append(line)
        
        if current_file:
            modules[current_file] = {
                'content': '\n'.join(current_content),
                'imports': self._get_imports('\n'.join(current_content)),
                'exports': self._get_exports('\n'.join(current_content)),
                'concepts': [],
                'complexity': 0
            }
        
        return modules
    
    def _get_imports(self, content: str) -> List[str]:

        imports = []
        patterns = [
            r'from\s+([\w.]+)\s+import',
            r'import\s+([\w.]+)',
            r'require\([\'"](.+?)[\'"]\)',
            r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]'
        ]
        
        for pattern in patterns:
            imports.extend(re.findall(pattern, content))
        
        return imports
    
    def _get_exports(self, content: str) -> List[str]:

        exports = []
        patterns = [
            r'class\s+(\w+)',
            r'def\s+(\w+)\s*\(',
            r'export\s+(?:class|function|const|let|var)\s+(\w+)',
            r'module\.exports\.(\w+)',
            r'exports\.(\w+)'
        ]
        
        for pattern in patterns:
            exports.extend(re.findall(pattern, content))
        
        return exports
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:

        dependencies = defaultdict(set)
        
        for module, info in self.modules.items():
            for imp in info['imports']:
                # Try to find which internal module this import refers to
                for other_module in self.modules:
                    if other_module != module:
# Works, but could be neater
                        if (imp in other_module or 
                            any(exp in imp for exp in self.modules[other_module]['exports'])):
                            dependencies[module].add(other_module)
        
        return dict(dependencies)
    
    def _calculate_complexity(self) -> Dict[str, int]:

        complexity = {}
        
        for module, info in self.modules.items():
            score = 0
            content = info['content']
            
            # Lines of code
            loc = len([line for line in content.split('\n') if line.strip()])
            score += min(loc // 50, 10)  # Max 10 points for size
            
            # Cyclomatic complexity (simplified)
            control_structures = len(re.findall(r'\b(if|for|while|except|elif|else)\b', content))
            score += min(control_structures // 5, 10)  # Max 10 points for control flow
            
            # Number of functions/classes
            functions = len(re.findall(r'def\s+\w+\s*\(', content))
            classes = len(re.findall(r'class\s+\w+', content))
            score += min((functions + classes * 2) // 5, 10)  # Max 10 points
            
            # Nesting depth
            max_indent = 0
            for line in content.split('\n'):
                if line.strip():
                    indent = len(line) - len(line.lstrip())
                    max_indent = max(max_indent, indent // 4)
            score += min(max_indent, 5)  # Max 5 points for nesting
            
            complexity[module] = score
            self.modules[module]['complexity'] = score
        
        return complexity
    
    def _get_concepts(self) -> Dict[str, List[str]]:

        concepts = defaultdict(list)
        
        concept_patterns = {
            'authentication': r'auth|login|password|token|session',
            'database': r'database|query|model|schema|migration',
            'api': r'api|endpoint|route|request|response',
            'frontend': r'component|render|state|props|view',
            'testing': r'test|spec|mock|assert|expect',
            'async': r'async|await|promise|callback|then',
            'error_handling': r'try|except|catch|error|exception',
            'validation': r'validat|check|verify|sanitiz',
            'caching': r'cache|redis|memcache|storage',
            'security': r'encrypt|decrypt|hash|salt|secure',
            'configuration': r'config|settings|env|environment',
            'logging': r'log|logger|debug|info|warn|error',
            'middleware': r'middleware|intercept|filter|hook',
            'websocket': r'websocket|socket|realtime|emit',
            'file_handling': r'file|upload|download|stream|buffer'
        }
        
        for module, info in self.modules.items():
            module_concepts = []
            content_lower = info['content'].lower()
            
            for concept, pattern in concept_patterns.items():
                if re.search(pattern, content_lower):
                    module_concepts.append(concept)
                    concepts[concept].append(module)
            
            self.modules[module]['concepts'] = module_concepts
        
        return dict(concepts)
    
    def generate_learning_path(self, goal: str = 'general', 
                             experience_level: str = 'beginner') -> List[Dict[str, Any]]:

        if goal == 'general':
            return self._generate_general_path(experience_level)
        elif goal == 'feature':
            return self._generate_feature_path(experience_level)
        elif goal == 'debugging':
            return self._generate_debugging_path(experience_level)
        elif goal == 'architecture':
            return self._generate_architecture_path(experience_level)
        else:
            return self._generate_general_path(experience_level)
    
    def _generate_general_path(self, level: str) -> List[Dict[str, Any]]:

        path = []
        
        # Step 1: Entry points
        entry_points = self._find_entry_points()
        path.append({
            'step': 1,
            'title': 'Understanding Entry Points',
            'description': 'Start by understanding how the application begins',
            'modules': entry_points[:3],
            'concepts': ['configuration', 'initialization'],
            'tasks': [
                'Identify the main entry file',
                'Understand the initialization sequence',
                'Note configuration loading'
            ]
        })
        
        # Step 2: Core concepts
        if level == 'beginner':
            core_modules = self._find_simple_modules()
            path.append({
                'step': 2,
                'title': 'Core Concepts and Simple Modules',
                'description': 'Learn the basic building blocks',
                'modules': core_modules[:5],
                'concepts': ['basic_structures', 'simple_logic'],
                'tasks': [
                    'Read through utility functions',
                    'Understand basic data structures',
                    'Identify common patterns'
                ]
            })
        
        # Step 3: Data flow
        path.append({
            'step': 3,
            'title': 'Understanding Data Flow',
            'description': 'Trace how data moves through the system',
            'modules': self._find_data_flow_modules()[:5],
            'concepts': ['api', 'database', 'validation'],
            'tasks': [
                'Follow a request from entry to response',
                'Understand data transformations',
                'Identify validation points'
            ]
        })
        
        # Step 4: Business logic
        business_modules = self._find_business_logic_modules()
        path.append({
            'step': 4,
            'title': 'Core Business Logic',
            'description': 'Understand the main functionality',
            'modules': business_modules[:5],
            'concepts': ['services', 'controllers', 'models'],
            'tasks': [
                'Identify key business rules',
                'Understand service interactions',
                'Map feature implementations'
            ]
        })
        
        # Step 5: Advanced topics
        if level != 'beginner':
            path.append({
                'step': 5,
                'title': 'Advanced Topics',
                'description': 'Deep dive into complex areas',
                'modules': self._find_complex_modules()[:5],
                'concepts': ['async', 'caching', 'security'],
                'tasks': [
                    'Understand async patterns',
                    'Review security implementations',
                    'Analyze performance optimizations'
                ]
            })
        
        return path
    
    def _generate_feature_path(self, level: str) -> List[Dict[str, Any]]:

        path = []
        
        # Find examples of complete features
        feature_examples = self._find_feature_examples()
        
        path.append({
            'step': 1,
            'title': 'Analyze Existing Features',
            'description': 'Study how features are currently implemented',
            'modules': feature_examples[:3],
            'concepts': ['patterns', 'structure'],
            'tasks': [
                'Pick a simple feature to study',
                'Trace its implementation end-to-end',
                'Note the files and patterns involved'
            ]
        })
        
        path.append({
            'step': 2,
            'title': 'Understand the Stack',
            'description': 'Learn each layer of the application',
            'modules': self._get_stack_modules(),
            'concepts': ['frontend', 'api', 'database'],
            'tasks': [
                'Identify each layer\'s responsibilities',
                'Understand inter-layer communication',
                'Note common patterns in each layer'
            ]
        })
        
        path.append({
            'step': 3,
            'title': 'Practice with Modifications',
            'description': 'Make small changes to existing features',
            'modules': feature_examples[:2],
            'concepts': ['modification', 'testing'],
            'tasks': [
                'Add a field to an existing model',
                'Create a new API endpoint',
                'Add validation to an existing feature'
            ]
        })
        
        return path
    
    def _generate_debugging_path(self, level: str) -> List[Dict[str, Any]]:

        path = []
        
        path.append({
            'step': 1,
            'title': 'Understanding Error Handling',
            'description': 'Learn how errors are handled',
            'modules': self._find_error_handling_modules()[:5],
            'concepts': ['error_handling', 'logging'],
            'tasks': [
                'Find error handling patterns',
                'Understand logging setup',
                'Identify common error types'
            ]
        })
        
        path.append({
            'step': 2,
            'title': 'Tracing Execution Flow',
            'description': 'Learn to follow code execution',
            'modules': self._find_entry_points()[:3],
            'concepts': ['flow_control', 'debugging'],
            'tasks': [
                'Set up debugging environment',
                'Place strategic breakpoints',
                'Trace a request through the system'
            ]
        })
        
        path.append({
            'step': 3,
            'title': 'Common Issues and Solutions',
            'description': 'Learn about common problems',
            'modules': self._find_complex_modules()[:3],
            'concepts': ['troubleshooting', 'performance'],
            'tasks': [
                'Review past bug fixes',
                'Understand performance bottlenecks',
                'Learn debugging tools and techniques'
            ]
        })
        
        return path
    
    def _generate_architecture_path(self, level: str) -> List[Dict[str, Any]]:

        path = []
        
        path.append({
            'step': 1,
            'title': 'High-Level Overview',
            'description': 'Understand the system architecture',
            'modules': self._find_architectural_modules()[:5],
            'concepts': ['architecture', 'design_patterns'],
            'tasks': [
                'Identify architectural patterns',
                'Map component relationships',
                'Understand design decisions'
            ]
        })
        
        path.append({
            'step': 2,
            'title': 'Component Deep Dive',
            'description': 'Understand each major component',
            'modules': self._find_core_components()[:5],
            'concepts': ['components', 'interfaces'],
            'tasks': [
                'Study component interfaces',
                'Understand component responsibilities',
                'Map inter-component communication'
            ]
        })
        
        path.append({
            'step': 3,
            'title': 'Integration Points',
            'description': 'Learn how components integrate',
            'modules': self._find_integration_modules()[:5],
            'concepts': ['integration', 'api', 'events'],
            'tasks': [
                'Identify integration patterns',
                'Understand data contracts',
                'Review event flows'
            ]
        })
        
        return path
    
    def _find_entry_points(self) -> List[str]:

        entry_patterns = [
            'main.py', 'app.py', 'index.py', 'server.py',
            'index.js', 'app.js', 'main.js', 'server.js',
            '__init__.py', 'manage.py', 'run.py'
        ]
        
        entries = []
        for module in self.modules:
            filename = module.split('/')[-1].lower()
            if filename in entry_patterns or 'main' in filename:
                entries.append(module)
        
        # Sort by likelihood of being main entry
        entries.sort(key=lambda x: (
            'main' not in x.lower(),
            'app' not in x.lower(),
            'index' not in x.lower()
        ))
        
        return entries
    
    def _find_simple_modules(self) -> List[str]:

        simple = []
        
        for module, info in self.modules.items():
            if (info['complexity'] < 15 and 
                len(info['imports']) < 5 and
                'util' in module.lower() or 'helper' in module.lower()):
                simple.append(module)
        
        # Sort by complexity
        simple.sort(key=lambda x: self.modules[x]['complexity'])
        
        return simple
    
    def _find_complex_modules(self) -> List[str]:

        complex_modules = [
            module for module, info in self.modules.items()
            if info['complexity'] > 20
        ]
        
        # Sort by complexity (descending)
        complex_modules.sort(key=lambda x: self.modules[x]['complexity'], reverse=True)
        
        return complex_modules
    
    def _find_data_flow_modules(self) -> List[str]:

        data_modules = []
        
        for module, info in self.modules.items():
            if any(concept in info['concepts'] for concept in ['api', 'database', 'validation']):
                data_modules.append(module)
        
        return data_modules
    
    def _find_business_logic_modules(self) -> List[str]:

        business_modules = []
        
        patterns = ['service', 'controller', 'handler', 'manager', 'processor']
        for module in self.modules:
            if any(pattern in module.lower() for pattern in patterns):
                business_modules.append(module)
        
        return business_modules
    
    def _find_feature_examples(self) -> List[str]:

        # Look for modules that have both API and model definitions
        features = []
        
        for module, info in self.modules.items():
            if ('api' in info['concepts'] or 'controller' in module.lower()) and \
               ('model' in module.lower() or 'database' in info['concepts']):
                features.append(module)
        
        return features
    
    def _get_stack_modules(self) -> List[str]:

        stack = []
        
        # Frontend
        for module in self.modules:
            if 'component' in module.lower() or 'view' in module.lower():
                stack.append(module)
                break
        
        # API
        for module in self.modules:
            if 'route' in module.lower() or 'api' in module.lower():
                stack.append(module)
                break
        
        # Business logic
        for module in self.modules:
            if 'service' in module.lower():
                stack.append(module)
                break
        
        # Database
        for module in self.modules:
            if 'model' in module.lower() or 'schema' in module.lower():
                stack.append(module)
                break
        
        return stack
    
    def _find_error_handling_modules(self) -> List[str]:

        return [
            module for module, info in self.modules.items()
            if 'error_handling' in info['concepts']
        ]
    
    def _find_architectural_modules(self) -> List[str]:

        arch_modules = []
        
        # Config and setup modules
        for module in self.modules:
            if 'config' in module.lower() or 'setup' in module.lower():
                arch_modules.append(module)
        
        # Main application modules
        arch_modules.extend(self._find_entry_points()[:2])
        
        return arch_modules
    
    def _find_core_components(self) -> List[str]:

        # Look for modules with high connectivity
        connectivity = defaultdict(int)
        
        for module, deps in self.dependencies.items():
            connectivity[module] += len(deps)
            for dep in deps:
                connectivity[dep] += 1
        
        # Sort by connectivity
        sorted_modules = sorted(connectivity.items(), key=lambda x: x[1], reverse=True)
        
        return [module for module, _ in sorted_modules[:10]]
    
    def _find_integration_modules(self) -> List[str]:

        integration_modules = []
        
        patterns = ['integration', 'adapter', 'connector', 'bridge', 'gateway']
        for module in self.modules:
            if any(pattern in module.lower() for pattern in patterns):
                integration_modules.append(module)
        
        # Also include modules with external API calls
        for module, info in self.modules.items():
            if 'websocket' in info['concepts'] or \
               re.search(r'fetch|axios|requests|http', info['content']):
                if module not in integration_modules:
                    integration_modules.append(module)
        
        return integration_modules
    
    def generate_module_study_guide(self, module_path: str) -> str:

        if module_path not in self.modules:
            return f"Module {module_path} not found"
        
        info = self.modules[module_path]
        guide = f"# Study Guide: {module_path}\n\n"
        
        # Overview
        guide += "## Overview\n"
        guide += f"- **Complexity Score**: {info['complexity']}/35\n"
        guide += f"- **Concepts**: {', '.join(info['concepts'])}\n"
        guide += f"- **Imports**: {len(info['imports'])} modules\n"
        guide += f"- **Exports**: {len(info['exports'])} items\n\n"
        
        # Prerequisites
        guide += "## Prerequisites\n"
        if info['imports']:
            guide += "Before studying this module, understand:\n"
            for imp in info['imports'][:5]:
                guide += f"- {imp}\n"
        else:
            guide += "This module has minimal dependencies.\n"
        guide += "\n"
        
        # Key components
        guide += "## Key Components\n"
        
        # Classes
        classes = re.findall(r'class\s+(\w+)', info['content'])
        if classes:
            guide += "### Classes\n"
            for cls in classes[:10]:
                guide += f"- `{cls}`\n"
            guide += "\n"
        
        # Functions
        functions = re.findall(r'def\s+(\w+)\s*\(', info['content'])
        if functions:
            guide += "### Functions\n"
            for func in functions[:10]:
                guide += f"- `{func}()`\n"
            guide += "\n"
        
        # Study approach
        guide += "## Study Approach\n"
        guide += "1. **First Pass**: Read through to understand overall structure\n"
        guide += "2. **Identify Patterns**: Look for common patterns used\n"
        guide += "3. **Trace Data Flow**: Follow how data moves through the module\n"
        guide += "4. **Understand Dependencies**: See how it connects to other modules\n"
        guide += "5. **Test Understanding**: Try to explain what each part does\n\n"
        
        # Exercises
        guide += "## Exercises\n"
        guide += "1. Draw a diagram of the module's main components\n"
        guide += "2. Write a summary of what this module does\n"
        guide += "3. Identify one function and trace its execution\n"
        guide += "4. Find where this module is used in the codebase\n"
        guide += "5. Suggest one improvement to the module\n"
        
        return guide
    
    def recommend_next_modules(self, completed_modules: List[str]) -> List[str]:

        recommendations = []
        completed_set = set(completed_modules)
        
        # Find modules that import completed modules
        for module, info in self.modules.items():
            if module not in completed_set:
# FIXME: refactor when time permits
                module_deps = set()
                for imp in info['imports']:
                    for completed in completed_modules:
                        if imp in completed or completed in imp:
                            module_deps.add(completed)
                
                if module_deps and len(module_deps) >= len(info['imports']) * 0.5:
                    recommendations.append(module)
        
        # Sort by complexity (easier first)
        recommendations.sort(key=lambda x: self.modules[x]['complexity'])
        
        return recommendations[:5]