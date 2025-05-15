"""
Analysis Pipeline Module for CodeLve
Handles the main analysis routing and framework-agnostic pipeline logic
"""

from pathlib import Path
import time
import torch

class AnalysisPipeline:

    
    def __init__(self, ai_client, framework_detector):
    # Works, but could be neater
        self.ai_client = ai_client
        self.framework_detector = framework_detector
    
    def framework_agnostic_analysis_pipeline(self, query, codebase_context):

        try:
            query_lower = query.lower()
            detected_framework = self.framework_detector.detect_framework_or_language(codebase_context)
            
            # INTELLIGENT ANALYSIS ROUTING (Framework Agnostic)
            
            # 1. Component/Class Analysis - WITH ARCHITECTURE
            if self._is_component_or_class_query(query_lower):
                entity_name = self._get_entity_name(query, detected_framework)
                if entity_name:
                    from .entity_analyzer import EntityAnalyzer
                    analyzer = EntityAnalyzer(self.framework_detector)
                    return analyzer.check_entity_with_architecture(query, codebase_context, entity_name, detected_framework)
            
            # 2. Module/Package Analysis
            if self._is_module_query(query_lower):
                module_path = self._get_module_path(query)
                if module_path:
                    from .search_utilities import SearchUtilities
                    search_utils = SearchUtilities(self.framework_detector)
                    return search_utils.check_module(query, codebase_context, module_path, detected_framework)
            
            # 3. Function/Method Analysis
            if self._is_function_or_method_query(query_lower):
                function_info = self._get_function_info(query)
                if function_info:
                    from .search_utilities import SearchUtilities
                    search_utils = SearchUtilities(self.framework_detector)
                    return search_utils.check_function_or_method(query, codebase_context, function_info, detected_framework)
            
            # 4. File Analysis
            if self._is_file_query(query_lower):
                file_name = self._get_file_name(query)
                if file_name:
                    from .search_utilities import SearchUtilities
                    search_utils = SearchUtilities(self.framework_detector)
                    return search_utils.check_file(query, codebase_context, file_name, detected_framework)
            
            # 5. Search Queries
            if self._is_search_query(query_lower):
                search_term = self._get_search_term(query)
                if search_term:
                    from .search_utilities import SearchUtilities
                    search_utils = SearchUtilities(self.framework_detector)
                    return search_utils.search_codebase(codebase_context, search_term, detected_framework)
            
            # 6. Architecture Analysis
            if any(word in query_lower for word in ['architecture', 'structure', 'overview', 'map', 'diagram']):
                from .architecture_analyzer import ArchitectureAnalyzer
                arch_analyzer = ArchitectureAnalyzer(self.framework_detector)
                return arch_analyzer.check_codebase_architecture(codebase_context, detected_framework)
            
            # 7. AI Model Response (Fallback)
            if self.ai_client.model and self.ai_client.tokenizer:
                return self._generate_ai_response(query, codebase_context)
            else:
                return self._get_fallback_suggestions(query, codebase_context, detected_framework)
                
        except Exception as e:
            return f"
    
    # QUERY TYPE DETECTION (Framework Agnostic)
    
    def _is_component_or_class_query(self, query_lower):

        entity_indicators = ['component', 'class', 'struct', 'interface', 'module', 'service', 'controller']
        action_words = ['explain', 'analyze', 'show', 'describe', 'what is', 'how does', 'teach', 'guide']
        
        return (any(indicator in query_lower for indicator in entity_indicators) and 
                any(action in query_lower for action in action_words))
    
    def _is_function_or_method_query(self, query_lower):

        return (any(keyword in query_lower for keyword in ['function', 'method', 'func', 'def']) or 
                'from' in query_lower and any(word in query_lower for word in ['explain', 'show', 'analyze']))
    
    def _is_file_query(self, query_lower):

        file_indicators = ['file', 'analyze', 'show', 'explain']
        return any(indicator in query_lower for indicator in file_indicators) and '.' in query_lower
    
    def _is_search_query(self, query_lower):

        search_words = ['find', 'search', 'list', 'show all', 'locate']
        return any(word in query_lower for word in search_words)
    
    def _is_module_query(self, query_lower):

        module_indicators = ['module', 'directory', 'folder', 'package', 'namespace', 'feature']
        return any(indicator in query_lower for indicator in module_indicators)
    
    # EXTRACTION METHODS (Framework Agnostic)
    
    def _get_entity_name(self, query, framework):

        words = query.split()
        
        # Look for word before entity type keywords
        entity_keywords = ['component', 'class', 'struct', 'interface', 'module', 'service']
        for i, word in enumerate(words):
            if word.lower() in entity_keywords and i > 0:
                return words[i-1].strip('.,!?')
        
        # Look for file extensions specific to frameworks
        extensions = ['.tsx', '.jsx', '.vue', '.py', '.java', '.cs', '.cpp', '.go', '.rs']
        for word in words:
            if any(word.endswith(ext) for ext in extensions):
                return Path(word).stem
        
        # Look for capitalized words (likely class/component names)
        for word in words:
            if len(word) > 2 and word[0].isupper() and word.isalnum():
                return word
        
        return None
    
    def _get_function_info(self, query):

        if 'from' in query:
            parts = query.split('from')
            if len(parts) == 2:
                function_name = parts[0].strip()
                for word in ['explain', 'analyze', 'show', 'describe']:
                    function_name = function_name.replace(word, '').strip()
                file_name = parts[1].strip()
                return {'function': function_name, 'file': file_name}
        
        return None
    
    def _get_file_name(self, query):

        words = query.split()
        common_extensions = ['.js', '.ts', '.tsx', '.jsx', '.py', '.java', '.cs', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.vue', '.html', '.css']
        for word in words:
            if '.' in word and any(ext in word for ext in common_extensions):
                return word
        return None
    
    def _get_search_term(self, query):

        search_words = ['find', 'search', 'list', 'show', 'all', 'locate', 'get']
        words = query.split()
        filtered_words = [word for word in words if word.lower() not in search_words]
        return ' '.join(filtered_words) if filtered_words else None
    
    def _get_module_path(self, query):

        words = query.split()
        for word in words:
            if '/' in word or '\\' in word:
                return word
        return None
    
    def _generate_ai_response(self, query, codebase_context):

        try:
            prompt = f"Analyze this codebase and answer: {query}\n\nCode context:\n{codebase_context[:1000]}..."
            
            inputs = self.ai_client.tokenizer.encode(
                prompt, return_tensors='pt', max_length=self.ai_client.max_length, truncation=True)
            inputs = inputs.to(self.ai_client.device)
            
            with torch.no_grad():
                outputs = self.ai_client.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 100,
                    num_return_sequences=1,
                    temperature=0.7,
                    pad_token_id=self.ai_client.tokenizer.eos_token_id,
                    do_sample=True
                )
            
            response = self.ai_client.tokenizer.decode(
                outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            
            return f"
            
        except Exception as e:
            print(f"AI generation error: {str(e)}")
            return self._get_fallback_suggestions(query, codebase_context, "Multi-language")

    def _get_fallback_suggestions(self, query, codebase_context, framework):

        detected_framework = self.framework_detector.detect_framework_or_language(codebase_context)
        app_domain = self.framework_detector.determine_app_domain_agnostic(codebase_context)
        
        return f"""

**Your query:** "{query}"
**Detected Framework:** {detected_framework}
**Application Domain:** {app_domain}



### **Entity Analysis (Any Language/Framework):**
- `explain [EntityName] component` - Complete business workflow analysis
- `analyze UserService class` - Service layer business logic
- `teach me about PaymentController` - Controller functionality deep dive

### **Universal Discovery:**
- `find authentication` - All auth-related code across languages
- `find database operations` - All data access patterns
- `find api endpoints` - All API-related functionality
- `find validation logic` - All validation patterns

### **Cross-Language Analysis:**
- `find service layer` - All service implementations
- `find business logic` - Core business functionality
- `find error handling` - Exception management patterns



**{detected_framework} Detected - I can analyze:**
- {self.framework_detector.get_framework_specific_patterns(detected_framework)}
- Framework-specific best practices and patterns
- Architecture recommendations for {detected_framework}


- I work with ANY programming language or framework
- Ask about business workflows, not just technical implementation
- I explain WHY code exists, not just HOW it works
- I connect technical implementation to business value


- "explain AuthenticationService" → Complete auth workflow analysis
- "find payment processing" → All payment-related functionality
- "analyze error handling patterns" → Exception management across codebase

Ready to analyze your {detected_framework} codebase! 🚀
"""


class QueryRouter:

    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
    
    def route_query(self, query, codebase_context):

        query_lower = query.lower()
        detected_framework = self.framework_detector.detect_framework_or_language(codebase_context)
# Not the cleanest, but it does the job
        if any(word in query_lower for word in ['architecture', 'structure', 'overview']):
            return 'architecture'
        elif any(word in query_lower for word in ['component', 'class', 'service']):
            return 'entity'
        elif any(word in query_lower for word in ['find', 'search', 'locate']):
            return 'search'
        elif any(word in query_lower for word in ['function', 'method']):
            return 'function'
        else:
            return 'general'
    
    def get_analysis_priority(self, query, codebase_context):

        query_lower = query.lower()
        
        # High priority for architecture and complex analysis
        if any(word in query_lower for word in ['architecture', 'explain', 'analyze']):
            return 'high'
        elif any(word in query_lower for word in ['find', 'search']):
            return 'medium'
        else:
            return 'low'


class ContextAnalyzer:

    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
    
    def check_context_complexity(self, codebase_context):

        lines = codebase_context.split('\n')
        files_count = len([line for line in lines if line.startswith('filepath:///')])
        total_lines = len([line for line in lines if line.strip() and not line.startswith('filepath:///')])
        
        if files_count > 1000 or total_lines > 100000:
            return 'very_high'
        elif files_count > 500 or total_lines > 50000:
            return 'high'
        elif files_count > 100 or total_lines > 10000:
            return 'medium'
        else:
            return 'low'
    
    def get_dominant_file_types(self, codebase_context):

        file_types = {}
        lines = codebase_context.split('\n')
        
        for line in lines:
            if line.startswith('filepath:///'):
                file_path = line.replace('filepath:///', '').replace(' /// /// ///', '')
                file_ext = Path(file_path).suffix.lower()
                file_types[file_ext] = file_types.get(file_ext, 0) + 1
        
        # Sort by frequency
        sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
        return sorted_types[:5]  # Return top 5 file types
    
    def estimate_analysis_time(self, query, codebase_context):

        complexity = self.check_context_complexity(codebase_context)
        query_type = 'simple' if len(query.split()) < 5 else 'complex'
        
        time_estimates = {
            ('low', 'simple'): '< 5 seconds',
            ('low', 'complex'): '5-15 seconds',
            ('medium', 'simple'): '10-20 seconds',
            ('medium', 'complex'): '15-30 seconds',
            ('high', 'simple'): '20-45 seconds',
            ('high', 'complex'): '30-60 seconds',
            ('very_high', 'simple'): '45-90 seconds',
            ('very_high', 'complex'): '60-120 seconds'
        }
        
        return time_estimates.get((complexity, query_type), '30-60 seconds')


class ResponseFormatter:

    
    def __init__(self):
        pass
    
    def format_architecture_response(self, analysis_result):

        if not analysis_result or len(analysis_result) < 100:
            return "
        
        # Add timestamp and metadata
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"""
*Generated: {timestamp}*

{analysis_result}

---

"""
        return formatted
    
    def format_entity_response(self, analysis_result):

        if not analysis_result or len(analysis_result) < 100:
            return "
            
        return analysis_result  # Entity responses are already well-formatted
    
    def format_search_response(self, analysis_result):

        if not analysis_result or 'No matches found' in analysis_result:
            return f"
        
        return analysis_result
    
    def add_performance_info(self, response, start_time):

        elapsed_time = time.time() - start_time
        performance_note = f"\n\n---\n
        return response + performance_note