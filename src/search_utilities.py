"""
Search Utilities Module for CodeLve
Handles search functionality, file analysis, and utility methods
"""

import re
from pathlib import Path

class SearchUtilities:

    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
    
    def search_codebase(self, codebase_context, search_term, framework):

        print(f"
        
        matches = []
        lines = codebase_context.split('\n')
        current_file = ""
        
        for line_num, line in enumerate(lines):
            if line.startswith('filepath:///'):
                current_file = line.replace('filepath:///', '').replace(' /// /// ///', '')
                continue
            
            if search_term.lower() in line.lower():
                matches.append({
                    'file': current_file,
                    'line_num': line_num,
                    'content': line.strip(),
                    'context': self._get_line_context(lines, line_num, 2)
                })
        
        if not matches:
            return self._generate_search_suggestions(search_term, codebase_context, framework)
        
        return self._format_search_results(search_term, matches, framework)
    
    def check_file(self, query, codebase_context, file_name, framework):

        file_content = self._get_file_content(file_name, codebase_context)
        
        if not file_content:
            return f"
        
        # Import technical analyzer
        from .technical_analyzers import TechnicalAnalyzers
        tech_analyzer = TechnicalAnalyzers(self.framework_detector)
        
        # Analyze file
        technical_details = tech_analyzer.check_technical_details_agnostic(file_content, framework)
        file_stats = self._check_file_statistics(file_content)
        dependencies = self._check_file_dependencies(file_content, framework)
        
        return f"""# 📄 **File Analysis: {file_name}**


{file_stats}

## ⚙️ **Technical Details**
{technical_details}

## 🔗 **Dependencies & Imports**
{dependencies}

## 📋 **File Content Preview**
```
{file_content[:500]}{'...' if len(file_content) > 500 else ''}
```


{self._generate_file_insights(file_content, framework)}

---

**📈 Complexity:** {self._assess_file_complexity(file_content)}
"""

    def check_function_or_method(self, query, codebase_context, function_info, framework):

        function_name = function_info.get('function', '')
        file_name = function_info.get('file', '')
        
        # Find function in codebase
        function_content = self._find_function_in_codebase(function_name, file_name, codebase_context)
        
        if not function_content:
            return f"""

**Search Suggestions:**
• `find {function_name}` - Search for function references
• `analyze {file_name}` - Analyze the entire file
• `find function` - List all functions
"""
        
        return self._check_function_detailed(function_name, function_content, framework)
    
    def check_module(self, query, codebase_context, module_path, framework):

        module_files = self._find_module_files(module_path, codebase_context)
        
        if not module_files:
            return f"
        
        return self._check_module_structure(module_path, module_files, framework)
    
    def _get_line_context(self, lines, target_line, context_size):

        start = max(0, target_line - context_size)
        end = min(len(lines), target_line + context_size + 1)
        return lines[start:end]
    
    def _format_search_results(self, search_term, matches, framework):

        total_matches = len(matches)
        unique_files = len(set(match['file'] for match in matches))
        
        # Group matches by file
        files_with_matches = {}
        for match in matches:
            if match['file'] not in files_with_matches:
                files_with_matches[match['file']] = []
            files_with_matches[match['file']].append(match)
        
        # Format results
        result_lines = [f"
        result_lines.append(f"**Found:** {total_matches} matches in {unique_files} files")
        result_lines.append(f"**Framework:** {framework}")
        result_lines.append("")
        
        # Show top matches by file
        for file_path, file_matches in list(files_with_matches.items())[:8]:
            result_lines.append(f"## 📁 **{Path(file_path).name}**")
            result_lines.append(f"*Path: {file_path}*")
            
            for match in file_matches[:3]:  # Show top 3 matches per file
                result_lines.append(f"**Line {match['line_num']}:** `{match['content'][:100]}`")
            
            if len(file_matches) > 3:
                result_lines.append(f"*...and {len(file_matches) - 3} more matches*")
            result_lines.append("")
        
        # Add usage suggestions
        result_lines.append("
        result_lines.append(f"• `explain {search_term}` - Detailed analysis if it's a component")
        result_lines.append(f"• `analyze [filename]` - Analyze specific files")
        result_lines.append("• `architecture` - See how this fits in overall system")
        
        return '\n'.join(result_lines)
    
    def _generate_search_suggestions(self, search_term, codebase_context, framework):

        # Find similar terms
        suggestions = []
        words = set()
        
        for line in codebase_context.split('\n'):
            if not line.startswith('filepath:///'):
                words.update(word.strip('(){}[];,') for word in line.split() if len(word) > 2)
        
        # Find words similar to search term
        for word in words:
            if (search_term.lower()[:3] in word.lower() or 
                word.lower()[:3] in search_term.lower()) and word != search_term:
                suggestions.append(word)
        
        return f"""


{chr(10).join([f"• `{s}`" for s in list(set(suggestions))[:8]]) if suggestions else "• No similar terms found"}


• Try partial terms: `find auth` instead of `authentication`
• Use common keywords: `find service`, `find component`, `find api`
• Check spelling and try variations

## 📋 **Popular Search Terms for {framework}:**
{self._get_popular_search_terms(framework)}

**Framework Detected:** {framework}
"""

    def _get_popular_search_terms(self, framework):

        framework_lower = framework.lower()
        
        if 'react' in framework_lower:
            return "• `component`, `hook`, `state`, `props`, `jsx`"
        elif 'vue' in framework_lower:
            return "• `component`, `template`, `script`, `computed`, `method`"
        elif 'angular' in framework_lower:
            return "• `component`, `service`, `directive`, `module`, `injectable`"
        elif 'python' in framework_lower:
            return "• `class`, `function`, `import`, `def`, `service`"
        elif 'java' in framework_lower:
            return "• `class`, `method`, `interface`, `service`, `controller`"
        else:
            return "• `function`, `class`, `service`, `api`, `component`"
    
    def _get_file_content(self, file_name, codebase_context):

        lines = codebase_context.split('\n')
        file_content = []
        in_target_file = False
        
        for line in lines:
            if line.startswith('filepath:///'):
                current_file = line.replace('filepath:///', '').replace(' /// /// ///', '')
                in_target_file = file_name.lower() in current_file.lower()
                continue
            
            if in_target_file:
                file_content.append(line)
        
        return '\n'.join(file_content) if file_content else None
    
    def _check_file_statistics(self, file_content):

        lines = file_content.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith(('#', '//', '/*'))]
        comment_lines = [line for line in lines if line.strip().startswith(('#', '//', '/*'))]
        blank_lines = [line for line in lines if not line.strip()]
        
        return f"""• **Total Lines:** {len(lines)}
• **Code Lines:** {len(code_lines)}
• **Comment Lines:** {len(comment_lines)}
• **Blank Lines:** {len(blank_lines)}
• **Code Density:** {len(code_lines)/max(len(lines), 1)*100:.1f}%"""
    
    def _check_file_dependencies(self, file_content, framework):

        dependencies = []
        lines = file_content.split('\n')
        
        for line in lines:
            line_lower = line.strip().lower()
            if any(keyword in line_lower for keyword in ['import', 'require', 'include', 'using', 'from']):
                dependencies.append(line.strip())
        
        if not dependencies:
            return "• No external dependencies detected"
        
        external_deps = [dep for dep in dependencies if not ('./' in dep or '../' in dep)]
        internal_deps = [dep for dep in dependencies if './' in dep or '../' in dep]
        
        result = []
        if external_deps:
            result.append(f"• **External Dependencies:** {len(external_deps)} imports")
        if internal_deps:
            result.append(f"• **Internal Dependencies:** {len(internal_deps)} local imports")
        
        return '\n'.join(result)
    
    def _generate_file_insights(self, file_content, framework):

        insights = []
        content_lower = file_content.lower()
        
        # Complexity insights
        function_count = content_lower.count('function') + content_lower.count('def')
        if function_count > 10:
            insights.append("• **High Complexity** - Many functions suggest complex responsibilities")
        elif function_count > 5:
            insights.append("• **Medium Complexity** - Well-organized functional structure")
        else:
            insights.append("• **Simple Structure** - Focused, single-purpose file")
        
        # Framework-specific insights
        framework_lower = framework.lower()
        if 'react' in framework_lower and 'usestate' in content_lower:
            insights.append("• **React State Management** - Uses hooks for state")
        elif 'vue' in framework_lower and 'computed' in content_lower:
            insights.append("• **Vue Reactivity** - Implements computed properties")
        elif 'python' in framework_lower and 'class' in content_lower:
            insights.append("• **Python OOP** - Object-oriented design pattern")
        
        # Quality insights
        if 'test' in content_lower:
            insights.append("• **Testing** - Includes test-related code")
        if 'todo' in content_lower:
            insights.append("• **Development Notes** - Contains TODO items")
        
        return '\n'.join(insights) if insights else "• Standard file structure detected"
    
    def _determine_file_type(self, file_name, file_content):

        file_lower = file_name.lower()
        content_lower = file_content.lower()
        
        if 'component' in file_lower or 'component' in content_lower:
            return "UI Component"
        elif 'service' in file_lower or 'service' in content_lower:
            return "Service Layer"
        elif 'test' in file_lower or 'spec' in file_lower:
            return "Test File"
        elif 'config' in file_lower or 'configuration' in content_lower:
            return "Configuration File"
        elif 'util' in file_lower or 'helper' in file_lower:
            return "Utility Module"
        elif 'model' in file_lower or 'entity' in content_lower:
            return "Data Model"
        else:
            return "Source Code File"
    
    def _assess_file_complexity(self, file_content):

        complexity_indicators = ['{', '}', 'if', 'for', 'while', 'switch', 'function', 'class']
        complexity_score = sum(file_content.lower().count(indicator) for indicator in complexity_indicators)
        
        if complexity_score > 100:
            return "High"
        elif complexity_score > 50:
            return "Medium"
        else:
            return "Low"
    
    def _find_function_in_codebase(self, function_name, file_name, codebase_context):

        lines = codebase_context.split('\n')
        function_content = []
        in_target_file = not file_name  # If no file specified, search all
        in_function = False
        indent_level = 0
        
        for line in lines:
            if line.startswith('filepath:///'):
                current_file = line.replace('filepath:///', '').replace(' /// /// ///', '')
                in_target_file = not file_name or file_name.lower() in current_file.lower()
                continue
            
            if in_target_file:
# Quick workaround for now
                if (function_name.lower() in line.lower() and 
                    any(keyword in line.lower() for keyword in ['def', 'function', 'const', 'let'])):
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())
                    function_content = [line]
                    continue
                
                # Collect function content
                if in_function:
                    current_indent = len(line) - len(line.lstrip())
                    # Stop if we hit another function at same or less indentation
                    if (line.strip() and current_indent <= indent_level and 
                        any(keyword in line.lower() for keyword in ['def', 'function', 'class'])):
                        break
                    function_content.append(line)
        
        return '\n'.join(function_content) if function_content else None
    
    def _check_function_detailed(self, function_name, function_content, framework):

        # Import technical analyzer
        from .technical_analyzers import TechnicalAnalyzers
        tech_analyzer = TechnicalAnalyzers(self.framework_detector)
        
        lines = function_content.split('\n')
        technical_details = tech_analyzer.check_technical_details_agnostic(function_content, framework)
        
        return f"""# 🔧 **Function Analysis: {function_name}**

## 📋 **Function Overview**
**Framework:** {framework}
**Lines of Code:** {len(lines)}
**Function Type:** {self._determine_function_type(function_content, framework)}

## ⚙️ **Technical Details**
{technical_details}


```
{function_content}
```


{self._check_function_insights(function_content, framework)}


{self._generate_function_recommendations(function_content, framework)}

---

**📈 Quality Score:** {self._calculate_function_quality(function_content)}/100
"""
    
    def _determine_function_type(self, function_content, framework):

        content_lower = function_content.lower()
        
        if 'async' in content_lower:
            return "Asynchronous Function"
        elif 'return' in content_lower:
            return "Pure Function (with return value)"
        elif any(keyword in content_lower for keyword in ['print', 'console.log', 'echo']):
            return "Procedure (side effects)"
        else:
            return "Standard Function"
    
    def _check_function_insights(self, function_content, framework):

        insights = []
        content_lower = function_content.lower()
        
        if 'async' in content_lower and 'await' in content_lower:
            insights.append("• **Asynchronous Pattern** - Handles async operations properly")
        
        if 'try' in content_lower and 'catch' in content_lower:
            insights.append("• **Error Handling** - Includes exception management")
        
        if content_lower.count('if') > 3:
            insights.append("• **Complex Logic** - Multiple conditional branches")
        
        return '\n'.join(insights) if insights else "• Standard function implementation"
    
    def _generate_function_recommendations(self, function_content, framework):

        recommendations = []
        content_lower = function_content.lower()
        
        if 'todo' in content_lower:
            recommendations.append("• Complete TODO items before production")
        
        if 'console.log' in content_lower or 'print(' in content_lower:
            recommendations.append("• Remove debug statements before deployment")
        
        if len(function_content.split('\n')) > 20:
            recommendations.append("• Consider breaking into smaller functions")
        
        return '\n'.join(recommendations) if recommendations else "• Function follows good practices"
    
    def _assess_function_complexity(self, function_content):

        complexity_keywords = ['if', 'for', 'while', 'switch', 'try', 'catch']
        complexity_score = sum(function_content.lower().count(keyword) for keyword in complexity_keywords)
        
        if complexity_score > 10:
            return "High"
        elif complexity_score > 5:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_function_quality(self, function_content):

        score = 70  # Base score
        content_lower = function_content.lower()
        
        # Positive indicators
        if any(doc in content_lower for doc in ['/**', '"""', '///']):
            score += 15
        if 'try' in content_lower and 'catch' in content_lower:
            score += 10
        if 'return' in content_lower:
            score += 5
        
        # Negative indicators
        if 'todo' in content_lower:
            score -= 10
        if 'console.log' in content_lower or 'print(' in content_lower:
            score -= 5
        if len(function_content.split('\n')) > 30:
            score -= 10
        
        return max(0, min(100, score))
    
    def _find_module_files(self, module_path, codebase_context):

        module_files = []
        lines = codebase_context.split('\n')
        
        for line in lines:
            if line.startswith('filepath:///'):
                file_path = line.replace('filepath:///', '').replace(' /// /// ///', '')
                if module_path.lower() in file_path.lower():
                    module_files.append(file_path)
        
        return module_files
    
    def _check_module_structure(self, module_path, module_files, framework):

        return f"""# 📁 **Module Analysis: {module_path}**


**Framework:** {framework}
**Total Files:** {len(module_files)}

## 📄 **Files in Module:**
{chr(10).join([f"• {Path(f).name}" for f in module_files[:10]])}
{f"...and {len(module_files) - 10} more files" if len(module_files) > 10 else ""}


• **Organization:** {'Well-organized' if len(module_files) > 3 else 'Simple'} module structure
• **Scope:** {'Large' if len(module_files) > 10 else 'Medium' if len(module_files) > 5 else 'Small'} module
• **Purpose:** {self._determine_module_purpose(module_path, module_files)}

---

"""
    
    def _determine_module_purpose(self, module_path, module_files):

        path_lower = module_path.lower()
        
        if 'component' in path_lower:
            return "UI Components module"
        elif 'service' in path_lower:
            return "Business logic services"
        elif 'util' in path_lower or 'helper' in path_lower:
            return "Utility functions module"
        elif 'test' in path_lower:
            return "Testing module"
        else:
            return "General purpose module"