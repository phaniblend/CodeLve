"""
Query Analyzer Module for CodeLve
Routes queries to appropriate analyzers and handles query understanding
"""

import re
from pathlib import Path
from .advanced_query_processor import AdvancedQueryProcessor

class QueryAnalyzer:

    
    def __init__(self, entity_analyzer, architecture_analyzer):
        self.entity_analyzer = entity_analyzer
        self.architecture_analyzer = architecture_analyzer
        self.advanced_processor = None  # Will be initialized when needed
        
    def check_query(self, query, codebase_context, framework=None):

        query_lower = query.lower().strip()
        
        print(f"
        
        # Initialize advanced processor if needed
        if not self.advanced_processor:
            self.advanced_processor = AdvancedQueryProcessor(codebase_context)
# Works, but could be neater
        response_text, response_type = self.advanced_processor.process_query(query)
        if response_type != 'help':  # 'help' is returned for general/unhandled queries
            return {
                'analysis_type': 'advanced',
                'primary_result': response_text,
                'framework': framework,
                'can_enhance': False
            }
# Might need cleanup
        if any(keyword in query_lower for keyword in ['architecture', 'structure', 'overview', 'design', 'codebase']):
            print("🏗️ Architecture query detected")
            architecture_result = self.architecture_analyzer.check_codebase_architecture(codebase_context, framework)
            
            return {
                'analysis_type': 'architecture',
                'primary_result': architecture_result,
                'framework': framework,
                'can_enhance': True,
                'enhancement_prompt': self._create_architecture_enhancement_prompt(query, framework)
            }
# Might need cleanup
        if any(keyword in query_lower for keyword in ['explain', 'analyze', 'what is', 'how does', 'show me']):
# FIXME: refactor when time permits
            entity_name = self._get_entity_name(query, query_lower)
            
            if entity_name:
                print(f"
                
                # Use entity analyzer
                result = self.entity_analyzer.check_entity(entity_name, codebase_context, framework)
# Might need cleanup
                if isinstance(result, dict) and result.get('needs_deepseek'):
                    return {
                        'analysis_type': 'entity',
                        'primary_result': result['prompt'],
                        'entity_name': entity_name,
                        'framework': framework,
                        'can_enhance': True,
                        'needs_deepseek': True,
                        'enhancement_prompt': result['prompt']
                    }
                else:
                    return {
                        'analysis_type': 'entity',
                        'primary_result': result,
                        'entity_name': entity_name,
                        'framework': framework,
                        'can_enhance': False
                    }
# Might need cleanup
        if any(keyword in query_lower for keyword in ['find', 'search', 'locate', 'where is', 'list all']):
            return self._handle_search_query(query, query_lower, codebase_context)
# Works, but could be neater
        if any(keyword in query_lower for keyword in ['pattern', 'best practice', 'example', 'how to']):
            return self._handle_pattern_query(query, codebase_context, framework)
        
        # Default: general query
        return self._handle_general_query(query, codebase_context, framework)
    
    def _get_entity_name(self, query, query_lower):

        # First, check if there's a file path in the query
        # Look for patterns like src/..., src\..., or anything with file extensions
        path_patterns = [
            r'(src[/\\][^\s]+)',  # src/ or src\ followed by path
            r'([a-zA-Z0-9_\-/\\]+\.[a-zA-Z]+)',  # any path with extension
            r'(components[/\\][^\s]+)',  # components/ or components\ paths
            r'(pages[/\\][^\s]+)',  # pages/ or pages\ paths
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                # Found a path - return it as-is
                return match.group(1).strip()
        
        # No path found, extract entity name by removing command words
        entity_name = query
        
        # Remove command keywords
        command_keywords = ['explain', 'analyze', 'what is', 'how does', 'show me']
        for keyword in command_keywords:
            # Case-insensitive replacement
            entity_name = re.sub(rf'\b{keyword}\b', '', entity_name, flags=re.IGNORECASE)
        
        # Remove punctuation at the end
        entity_name = re.sub(r'[?!.]+$', '', entity_name)
        
        # Clean up extra spaces
        entity_name = ' '.join(entity_name.split()).strip()
        
        # Remove articles only if it's not a path
        if not ('/' in entity_name or '\\' in entity_name):
            articles = ['the', 'a', 'an']
            for article in articles:
                entity_name = re.sub(rf'\b{article}\b', '', entity_name, flags=re.IGNORECASE)
            
            # Remove type words only for non-paths
            type_words = ['component', 'class', 'function', 'module', 'file', 'service']
            for word in type_words:
                entity_name = re.sub(rf'\b{word}\b', '', entity_name, flags=re.IGNORECASE)
        
        # Final cleanup
        entity_name = ' '.join(entity_name.split()).strip()
        
        if entity_name and len(entity_name) > 2:
            return entity_name
        
        return None
    
    def _handle_search_query(self, query, query_lower, codebase_context):
# TODO: revisit this later
        search_term = query_lower
        for keyword in ['find', 'search', 'locate', 'where is', 'list all']:
            search_term = search_term.replace(keyword, '').strip()
        
        # Perform search
        results = self._search_codebase(search_term, codebase_context)
        
        return {
            'analysis_type': 'search',
            'primary_result': results,
            'search_term': search_term,
            'can_enhance': False
        }
    
    def _handle_pattern_query(self, query, codebase_context, framework):

        # Create a prompt for pattern analysis
        prompt = f"""Analyze the codebase and provide examples and best practices for: {query}

Focus on:
1. Existing patterns in this specific codebase
2. Code examples from actual files
3. Best practices followed in this project
4. Common patterns and conventions used

Provide specific file references and code snippets where relevant."""
        
        return {
            'analysis_type': 'pattern',
            'primary_result': prompt,
            'framework': framework,
            'can_enhance': True,
            'enhancement_prompt': prompt
        }
    
    def _handle_general_query(self, query, codebase_context, framework):

        # Create a general analysis prompt
        prompt = f"""Answer this question about the codebase: {query}

Provide a comprehensive answer based on:
1. The actual code structure and implementation
2. Specific examples from the codebase
3. Technical details relevant to the question
4. Business context where applicable

Use specific file references and code examples to support your answer."""
        
        return {
            'analysis_type': 'general',
            'primary_result': prompt,
            'framework': framework,
            'can_enhance': True,
            'enhancement_prompt': prompt
        }
    
    def _search_codebase(self, search_term, codebase_context):

        results = []
        lines = codebase_context.split('\n')
        current_file = ""
        
        for i, line in enumerate(lines):
            if line.startswith('filepath:///'):
                current_file = line.replace('filepath:///', '').strip()
                continue
            
            if search_term in line.lower():
                # Get context lines
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 3)
                context = lines[context_start:context_end]
                
                results.append({
                    'file': current_file,
                    'line': i,
                    'match': line.strip(),
                    'context': '\n'.join(context)
                })
                
                if len(results) >= 20:  # Limit results
                    break
        
        # Format results
        if not results:
            return f"No results found for '{search_term}'"
        
        formatted = f"
        formatted += f"Found {len(results)} matches:\n\n"
        
        for r in results[:10]:  # Show first 10
            formatted += f"**File:** `{r['file']}`\n"
            formatted += f"**Match:** {r['match']}\n"
            formatted += "```\n" + r['context'] + "\n```\n\n"
        
        if len(results) > 10:
            formatted += f"\n... and {len(results) - 10} more matches"
        
        return formatted
    
    def _create_architecture_enhancement_prompt(self, query, framework):

        return f"""Provide a detailed architectural analysis for this {framework or 'codebase'} answering: {query}

Focus on:
1. Overall system design and structure
2. Key architectural patterns and decisions
3. Module organization and dependencies
4. Data flow and component interactions
5. Best practices and recommendations

Use specific examples from the actual codebase."""
    
    def route_query(self, query, codebase_context, framework=None):

        query_lower = query.lower().strip()
        
        print(f"
# Might need cleanup
        if not framework:
            framework = self.architecture_analyzer.framework_detector.detect_framework_or_language(codebase_context)
        
        # Initialize advanced processor if needed
        if not self.advanced_processor:
            self.advanced_processor = AdvancedQueryProcessor(codebase_context)
# Might need cleanup
        response_text, response_type = self.advanced_processor.process_query(query)
        if response_type != 'help':  # 'help' is returned for general/unhandled queries
            print(f"✨ Advanced query type detected: {response_type}")
            return {
                'analysis_type': 'advanced',
                'primary_result': response_text,
                'framework': framework,
                'can_enhance': False  # Advanced queries are already enhanced
            }
        
        # Continue with standard routing
        return self.check_query(query, codebase_context, framework)