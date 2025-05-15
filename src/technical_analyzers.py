"""
Technical Analyzers Module for CodeLve
Provides technical analysis capabilities for code understanding
"""

import re
from pathlib import Path

class TechnicalAnalyzers:

    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
    
    def check_technical_details_agnostic(self, content, framework):

        details = []
        
        # Analyze code complexity
        complexity = self._check_complexity(content)
        details.append(f"**Complexity Score:** {complexity}/10")
        
        # Count key constructs
        constructs = self._count_constructs(content)
        details.append(f"**Key Constructs:**")
        for construct, count in constructs.items():
            if count > 0:
                details.append(f"  - {construct}: {count}")
        
        # Analyze patterns
        patterns = self._detect_patterns(content, framework)
        if patterns:
            details.append(f"**Patterns Detected:**")
            for pattern in patterns:
                details.append(f"  - {pattern}")
        
        return '\n'.join(details)
    
    def _check_complexity(self, content):

        lines = content.split('\n')
        
        # Simple complexity score based on various factors
        score = 0
        
        # Nesting depth
        max_indent = 0
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent)
        
        if max_indent > 20:
            score += 3
        elif max_indent > 12:
            score += 2
        elif max_indent > 8:
            score += 1
        
        # Control flow complexity
        control_keywords = ['if', 'else', 'elif', 'for', 'while', 'switch', 'case']
        control_count = sum(content.lower().count(keyword) for keyword in control_keywords)
        
        if control_count > 20:
            score += 3
        elif control_count > 10:
            score += 2
        elif control_count > 5:
            score += 1
        
        # File length
        if len(lines) > 500:
            score += 2
        elif len(lines) > 300:
            score += 1
        
        # Function/method count
        function_count = content.count('function') + content.count('def ') + content.count('const ')
        if function_count > 15:
            score += 2
        elif function_count > 8:
            score += 1
        
        return min(10, score)
    
    def _count_constructs(self, content):

        constructs = {
            'Functions': 0,
            'Classes': 0,
            'Conditionals': 0,
            'Loops': 0,
            'Try/Catch': 0,
            'Imports': 0
        }
        
        lines = content.split('\n')
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Functions
            if any(keyword in line_lower for keyword in ['function', 'def ', 'const ', '=>']):
                constructs['Functions'] += 1
            
            # Classes
            if any(keyword in line_lower for keyword in ['class ', 'interface ', 'struct ']):
                constructs['Classes'] += 1
            
            # Conditionals
            if any(keyword in line_lower for keyword in ['if ', 'else', 'switch']):
                constructs['Conditionals'] += 1
            
            # Loops
            if any(keyword in line_lower for keyword in ['for ', 'while ', 'do ']):
                constructs['Loops'] += 1
            
            # Error handling
            if any(keyword in line_lower for keyword in ['try', 'catch', 'except', 'finally']):
                constructs['Try/Catch'] += 1
            
            # Imports
            if any(keyword in line_lower for keyword in ['import ', 'require(', 'include']):
                constructs['Imports'] += 1
        
        return constructs
    
    def _detect_patterns(self, content, framework):

        patterns = []
        content_lower = content.lower()
        
        # React patterns
        if 'react' in framework.lower():
            if 'usestate' in content_lower:
                patterns.append("React Hooks - State Management")
            if 'useeffect' in content_lower:
                patterns.append("React Hooks - Side Effects")
            if 'usecontext' in content_lower:
                patterns.append("React Context API")
            if 'redux' in content_lower:
                patterns.append("Redux State Management")
        
        # General patterns
        if 'async' in content_lower and 'await' in content_lower:
            patterns.append("Async/Await Pattern")
        
        if 'observable' in content_lower or 'subscribe' in content_lower:
            patterns.append("Observer Pattern")
        
        if 'singleton' in content_lower:
            patterns.append("Singleton Pattern")
        
        if 'factory' in content_lower:
            patterns.append("Factory Pattern")
        
        # API patterns
        if 'rest' in content_lower or 'api' in content_lower:
            patterns.append("RESTful API Design")
        
        if 'graphql' in content_lower:
            patterns.append("GraphQL API")
        
        return patterns
    
    def check_dependencies(self, content):

        dependencies = {
            'external': [],
            'internal': []
        }
        
        lines = content.split('\n')
        
        for line in lines:
            if 'import' in line or 'require' in line:
# Might need cleanup
                if 'from' in line:
                    # Python style
                    match = re.search(r'from\s+(\S+)\s+import', line)
                    if match:
                        module = match.group(1)
                        if module.startswith('.'):
                            dependencies['internal'].append(module)
                        else:
                            dependencies['external'].append(module)
                elif 'import' in line:
                    # JS/TS style
                    match = re.search(r'from\s+[\'"]([^\'"]+)[\'"]', line)
                    if match:
                        module = match.group(1)
                        if module.startswith('.'):
                            dependencies['internal'].append(module)
                        else:
                            dependencies['external'].append(module)
        
        return dependencies
    
    def check_code_quality(self, content):

        quality_issues = []
        
        lines = content.split('\n')
# Might need cleanup
        for i, line in enumerate(lines):
            # Long lines
            if len(line) > 120:
                quality_issues.append(f"Line {i+1}: Line too long ({len(line)} chars)")
            
            # TODO comments
            if 'TODO' in line or 'FIXME' in line:
                quality_issues.append(f"Line {i+1}: Found TODO/FIXME comment")
            
            # Console logs
            if 'console.log' in line or 'print(' in line:
                quality_issues.append(f"Line {i+1}: Debug statement found")
        
        return quality_issues[:10]  # Limit to first 10 issues