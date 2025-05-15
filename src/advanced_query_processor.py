"""
Advanced Query Processor for CodeLve.
Orchestrates all query processing modules to handle complex code analysis requests.
"""

import re
from typing import Dict, List, Optional, Any, Tuple

from .query_processors import (
    CodeGenerator,
    DiagramGenerator,
    WalkthroughGenerator,
    PatternAnalyzer,
    ApiAnalyzer,
    LearningPathGenerator
)


class AdvancedQueryProcessor:

    
    def __init__(self, consolidated_code: str):
        self.consolidated_code = consolidated_code
        
        # Initialize all processors
        self.code_generator = CodeGenerator(consolidated_code)
        self.diagram_generator = DiagramGenerator(consolidated_code)
        self.walkthrough_generator = WalkthroughGenerator(consolidated_code)
        self.pattern_analyzer = PatternAnalyzer(consolidated_code)
        self.api_analyzer = ApiAnalyzer(consolidated_code)
        self.learning_path_generator = LearningPathGenerator(consolidated_code)
    
    def process_query(self, query: str) -> Tuple[str, str]:
        """
        Process a complex query and return the result.
        Returns: (response_text, response_type)
        """
        query_lower = query.lower()
# FIXME: refactor when time permits
# Not the cleanest, but it does the job
        if self._is_file_generation_query(query):
            try:
                from .query_processors.pattern_file_generator import generate_file_following_patterns
                result = generate_file_following_patterns(query, self.consolidated_code)
                return result, 'code_generation'
            except ImportError:
                return "Pattern file generator not available. Please check installation.", 'error'
        
        elif self._is_code_generation_query(query_lower):
            return self._handle_code_generation(query)
        
        elif self._is_diagram_query(query_lower):
            return self._handle_diagram_generation(query)
        
        elif self._is_walkthrough_query(query_lower):
            return self._handle_walkthrough_generation(query)
        
        elif self._is_pattern_analysis_query(query_lower):
            return self._handle_pattern_analysis(query)
        
        elif self._is_api_query(query_lower):
            return self._handle_api_analysis(query)
        
        elif self._is_learning_query(query_lower):
            return self._handle_learning_path(query)
        
        else:
            return self._handle_general_query(query)
    
    def _is_code_generation_query(self, query: str) -> bool:

        keywords = ['generate', 'create', 'scaffold', 'build', 'new component', 
                   'new feature', 'add endpoint', 'create model']
        return any(keyword in query for keyword in keywords)
    
    def _is_file_generation_query(self, query: str) -> bool:

        keywords = ['create a new section', 'create a new file', 'generate a file', 
                   'following the same pattern', 'following patterns', 'in the same pattern']
        return any(keyword in query.lower() for keyword in keywords)
    
    def _is_diagram_query(self, query: str) -> bool:

        keywords = ['diagram', 'visualize', 'architecture', 'flow chart', 
                   'dependency graph', 'class diagram', 'sequence diagram']
        return any(keyword in query for keyword in keywords)
    
    def _is_walkthrough_query(self, query: str) -> bool:

        keywords = ['walkthrough', 'guide', 'how to', 'step by step', 
                   'tutorial', 'implement', 'add feature']
        return any(keyword in query for keyword in keywords)
    
    def _is_pattern_analysis_query(self, query: str) -> bool:

        keywords = ['pattern', 'convention', 'style', 'anti-pattern', 
                   'best practice', 'naming', 'structure']
        return any(keyword in query for keyword in keywords)
    
    def _is_api_query(self, query: str) -> bool:

        keywords = ['api', 'endpoint', 'route', 'payload', 'request', 
                   'response', 'rest', 'http method']
        return any(keyword in query for keyword in keywords)
    
    def _is_learning_query(self, query: str) -> bool:

        keywords = ['learn', 'understand', 'study', 'where to start', 
                   'beginner', 'onboarding', 'explore']
        return any(keyword in query for keyword in keywords)
    
    def _parse_generation_query(self, query: str) -> Tuple[str, str, Optional[Dict]]:

        # Default values
        component_type = "component"
        component_name = "NewComponent"
        specs = {}
# Not the cleanest, but it does the job
        name_patterns = [
            r'(?:called|named)\s+["\']?(\w+)["\']?',
            r'component\s+["\']?(\w+)["\']?',
            r'create\s+(?:a\s+)?["\']?(\w+)["\']?'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                component_name = match.group(1)
                break
# Not the cleanest, but it does the job
        if 'service' in query.lower():
            component_type = 'service'
        elif 'model' in query.lower():
            component_type = 'model'
        elif 'api' in query.lower() or 'endpoint' in query.lower():
            component_type = 'api'
        elif 'test' in query.lower():
            component_type = 'test'
# Might need cleanup
        props_match = re.search(r'with\s+props?\s+["\']?([^"\'.]+)["\']?', query, re.IGNORECASE)
        if props_match:
            props_str = props_match.group(1)
            specs['props'] = [prop.strip() for prop in props_str.split(',')]
        
        return component_type, component_name, specs
    
    def _handle_code_generation(self, query: str) -> Tuple[str, str]:
# Not the cleanest, but it does the job
        try:
            from .query_processors.context_aware_generator import ContextAwareGenerator
            context_generator = ContextAwareGenerator(self.consolidated_code)
# Works, but could be neater
            component_type, component_name, specs = self._parse_generation_query(query)
            
            # Generate code based on existing patterns
            generated_code = context_generator.generate_component(component_name, specs)
            
            # Add explanation about the patterns used
            patterns_used = context_generator.get_patterns_used()
            
            response = f"# Generated {component_name} Component\n\n"
            response += "Based on your codebase analysis, I've generated this component following:\n"
            response += f"- **Component Style**: {patterns_used['style']}\n"
            response += f"- **State Management**: {patterns_used['state']}\n"
            response += f"- **Styling Method**: {patterns_used['styling']}\n"
            response += f"- **Common Patterns**: {', '.join(patterns_used['patterns'])}\n\n"
            response += f"```{patterns_used['language']}\n{generated_code}\n```\n\n"
            response += "This component follows the exact patterns found in your codebase."
            
            return response, 'code_generation'
        except ImportError:
            # Fallback to basic code generator
            return self._handle_basic_code_generation(query)
    
    def _handle_basic_code_generation(self, query: str) -> Tuple[str, str]:

        # Parse query
        component_match = re.search(r'(?:component|function|class)\s+(?:called\s+)?["\']?(\w+)["\']?', query, re.IGNORECASE)
        component_name = component_match.group(1) if component_match else 'NewComponent'
# TODO: revisit this later
        if 'function' in query.lower():
            code = self.code_generator.generate_function(component_name)
            response = f"# Generated Function: {component_name}\n\n```python\n{code}\n```"
        elif 'class' in query.lower():
            code = self.code_generator.generate_class(component_name)
            response = f"# Generated Class: {component_name}\n\n```python\n{code}\n```"
        else:
            # Default to component
            framework = self.code_generator.detect_framework()
            if framework == 'react':
                code = self.code_generator.generate_react_component(component_name)
                response = f"# Generated React Component: {component_name}\n\n```javascript\n{code}\n```"
            elif framework == 'vue':
                code = self.code_generator.generate_vue_component(component_name)
                response = f"# Generated Vue Component: {component_name}\n\n```vue\n{code}\n```"
            else:
                code = self.code_generator.generate_generic_component(component_name)
                response = f"# Generated Component: {component_name}\n\n```javascript\n{code}\n```"
        
        return response, 'code_generation'
    
    def _handle_diagram_generation(self, query: str) -> Tuple[str, str]:

        diagram_type = 'architecture'
        module_name = None
# Might need cleanup
        if 'dependency' in query.lower():
            diagram_type = 'dependency'
        elif 'class' in query.lower():
            diagram_type = 'class'
        elif 'sequence' in query.lower():
            diagram_type = 'sequence'
        elif 'flow' in query.lower():
            diagram_type = 'flow'
# TODO: revisit this later
        module_match = re.search(r'(?:for|of)\s+["\']?(\S+)["\']?', query)
        if module_match:
            module_name = module_match.group(1)
        
        # Generate appropriate diagram
        if diagram_type == 'architecture':
            mermaid_code = self.diagram_generator.generate_architecture_diagram()
        elif diagram_type == 'dependency':
            mermaid_code = self.diagram_generator.generate_dependency_graph(module_name)
        elif diagram_type == 'class':
            mermaid_code = self.diagram_generator.generate_class_diagram(module_name)
        elif diagram_type == 'sequence':
            scenario = query  # Use full query as scenario
            mermaid_code = self.diagram_generator.generate_sequence_diagram(scenario)
        elif diagram_type == 'flow':
            process_name = module_name or 'Process'
            mermaid_code = self.diagram_generator.generate_flow_diagram(process_name)
        else:
            mermaid_code = self.diagram_generator.generate_architecture_diagram()
        
        response = f"# {diagram_type.title()} Diagram\n\n"
        response += "```mermaid\n"
        response += mermaid_code
        response += "\n```\n\n"
        response += "You can render this diagram using any Mermaid-compatible viewer."
        
        return response, 'diagram'
    
    def _handle_walkthrough_generation(self, query: str) -> Tuple[str, str]:
# Might need cleanup
        feature_type = 'generic'
        feature_name = 'NewFeature'
        
        if 'api' in query.lower() or 'endpoint' in query.lower():
            feature_type = 'api_endpoint'
        elif 'model' in query.lower() or 'database' in query.lower():
            feature_type = 'database_model'
        elif 'component' in query.lower() or 'frontend' in query.lower():
            feature_type = 'frontend_component'
        elif 'auth' in query.lower():
            feature_type = 'authentication'
        elif 'test' in query.lower():
            feature_type = 'test'
# TODO: revisit this later
        name_match = re.search(r'(?:called|named|for)\s+["\']?(\w+)["\']?', query)
        if name_match:
            feature_name = name_match.group(1)
# Quick workaround for now
        if 'understand' in query.lower() or 'explain' in query.lower():
            walkthrough = self.walkthrough_generator.generate_understanding_walkthrough(feature_name)
        else:
            walkthrough = self.walkthrough_generator.generate_feature_walkthrough(feature_name, feature_type)
        
        return walkthrough, 'walkthrough'
    
    def _handle_pattern_analysis(self, query: str) -> Tuple[str, str]:

        if 'anti-pattern' in query.lower() or 'issue' in query.lower():
            anti_patterns = self.pattern_analyzer.find_anti_patterns()
            
            response = "# Code Anti-Patterns Found\n\n"
            if anti_patterns:
                for pattern in anti_patterns:
                    response += f"## {pattern['type'].replace('_', ' ').title()}\n"
                    response += f"- **Severity**: {pattern['severity']}\n"
                    response += f"- **Description**: {pattern['description']}\n"
                    response += f"- **Recommendation**: {pattern['recommendation']}\n"
                    if 'file' in pattern:
                        response += f"- **File**: {pattern['file']}\n"
                    response += "\n"
            else:
                response += "No significant anti-patterns found!\n"
            
            return response, 'analysis'
        
        elif 'naming' in query.lower():
            naming_patterns = self.pattern_analyzer.check_naming_patterns()
            
            response = "# Naming Convention Analysis\n\n"
            for category, patterns in naming_patterns.items():
                if isinstance(patterns, dict) and 'total' in patterns:
                    response += f"## {category.title()}\n"
                    response += f"- Total: {patterns['total']}\n"
                    if 'dominant_style' in patterns:
                        response += f"- Dominant style: **{patterns['dominant_style']}**\n"
                    if 'examples' in patterns and patterns['examples']:
                        response += f"- Examples: {', '.join(patterns['examples'][:5])}\n"
                    response += "\n"
            
            return response, 'analysis'
        
        else:
            # General pattern report
            report = self.pattern_analyzer.generate_pattern_report()
            return report, 'analysis'
    
    def _handle_api_analysis(self, query: str) -> Tuple[str, str]:

        if 'document' in query.lower():
            documentation = self.api_analyzer.generate_api_documentation()
            return documentation, 'documentation'
        
        elif 'issue' in query.lower() or 'problem' in query.lower():
            issues = self.api_analyzer.find_api_issues()
            
            response = "# API Design Issues\n\n"
            if issues:
                for issue in issues:
                    response += f"## {issue['type'].replace('_', ' ').title()}\n"
                    response += f"- **Severity**: {issue['severity']}\n"
                    response += f"- **Description**: {issue['description']}\n"
                    response += f"- **Recommendation**: {issue['recommendation']}\n"
                    if 'details' in issue:
                        response += f"- **Details**: {issue['details']}\n"
                    response += "\n"
            else:
                response += "No significant API issues found!\n"
            
            return response, 'analysis'
        
        elif 'endpoint' in query.lower() and ('analyze' in query.lower() or 'explain' in query.lower()):
# Might need cleanup
            path_match = re.search(r'["\']?(/[\w/{}]+)["\']?', query)
            if path_match:
                endpoint_path = path_match.group(1)
                analysis = self.api_analyzer.check_endpoint_interactions(endpoint_path)
                
                response = f"# Endpoint Analysis: {endpoint_path}\n\n"
                if 'error' not in analysis:
                    response += f"- **Methods**: {', '.join(analysis['endpoint']['methods'])}\n"
                    response += f"- **Handler**: `{analysis['endpoint']['handler']}`\n"
                    response += f"- **Type**: {analysis['endpoint']['type']}\n\n"
                    
                    if analysis['request_model']:
                        response += "## Request Model\n"
                        response += f"- **Name**: {analysis['request_model']['name']}\n"
                        response += "- **Fields**:\n"
                        for field in analysis['request_model'].get('fields', []):
                            response += f"  - `{field['name']}`: {field['type']}\n"
                        response += "\n"
                    
                    if analysis['database_operations']:
                        response += f"## Database Operations\n"
                        response += f"{', '.join(analysis['database_operations'])}\n\n"
                else:
                    response += "Endpoint not found.\n"
                
                return response, 'analysis'
        
        # Default API structure analysis
        api_structure = self.api_analyzer.check_api_structure()
        
        response = "# API Structure Analysis\n\n"
        response += f"- **Total Endpoints**: {api_structure['total_endpoints']}\n"
        response += f"- **Frameworks**: {', '.join(api_structure['frameworks_used'])}\n"
        response += f"- **RESTful Compliance**: {api_structure['restful_analysis']['compliance_score']}%\n\n"
        
        response += "## Endpoints by Method\n"
        for method, count in api_structure['endpoints_by_method'].items():
            response += f"- {method}: {count}\n"
        response += "\n"
        
        response += "## Endpoints by Type\n"
        for endpoint_type, count in api_structure['endpoints_by_type'].items():
            response += f"- {endpoint_type}: {count}\n"
        
        return response, 'analysis'
    
    def _handle_learning_path(self, query: str) -> Tuple[str, str]:
# Might need cleanup
        goal = 'general'
        level = 'beginner'
        
        if 'feature' in query.lower():
            goal = 'feature'
        elif 'debug' in query.lower():
            goal = 'debugging'
        elif 'architect' in query.lower():
            goal = 'architecture'
        
        if 'advanced' in query.lower() or 'expert' in query.lower():
            level = 'advanced'
        elif 'intermediate' in query.lower():
            level = 'intermediate'
# TODO: revisit this later
        module_match = re.search(r'(?:module|file)\s+["\']?(\S+)["\']?', query)
        if module_match:
            module_name = module_match.group(1)
            study_guide = self.learning_path_generator.generate_module_study_guide(module_name)
            return study_guide, 'learning'
        
        # Generate learning path
        learning_path = self.learning_path_generator.generate_learning_path(goal, level)
        
        response = f"# Learning Path: {goal.title()} ({level.title()} Level)\n\n"
        
        for step in learning_path:
            response += f"## Step {step['step']}: {step['title']}\n"
            response += f"{step['description']}\n\n"
            
            if step.get('modules'):
                response += "**Modules to study:**\n"
                for module in step['modules']:
                    response += f"- `{module}`\n"
                response += "\n"
            
            if step.get('concepts'):
                response += f"**Key concepts:** {', '.join(step['concepts'])}\n\n"
            
            if step.get('tasks'):
                response += "**Tasks:**\n"
                for task in step['tasks']:
                    response += f"- {task}\n"
                response += "\n"
            
            response += "---\n\n"
        
        return response, 'learning'
    
    def _handle_general_query(self, query: str) -> Tuple[str, str]:

        response = "I can help you with:\n\n"
        response += "1. **Code Generation** - Generate new components following your patterns\n"
        response += "2. **Diagrams** - Create architecture, dependency, or flow diagrams\n"
        response += "3. **Walkthroughs** - Step-by-step guides for implementing features\n"
        response += "4. **Pattern Analysis** - Analyze code patterns and find anti-patterns\n"
        response += "5. **API Analysis** - Analyze endpoints, generate documentation\n"
        response += "6. **Learning Paths** - Get personalized learning paths for the codebase\n\n"
        response += "Try asking something like:\n"
        response += "- 'Generate a new API endpoint for users'\n"
        response += "- 'Create an architecture diagram'\n"
        response += "- 'How do I add a new feature?'\n"
        response += "- 'Analyze naming patterns'\n"
        response += "- 'Document the API endpoints'\n"
        response += "- 'Where should I start learning this codebase?'"
        
        return response, 'help'