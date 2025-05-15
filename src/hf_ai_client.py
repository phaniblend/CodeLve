"""
Main HuggingFace AI Client for CodeLve
Enhanced AI client with Dual-LLM Prompt Engineering Layer + Framework-Agnostic Analysis
"""

import torch
import time
import re
import json
from pathlib import Path

# Import our modular components
from .framework_detector import FrameworkDetector

class HuggingFaceAIClient:

    
    def __init__(self):
    # Might need cleanup
        # DUAL-LLM ARCHITECTURE - Optimized models for perfect quality/size balance
        self.prompt_engineer_model = "microsoft/DialoGPT-small"                    # 117MB - Fast prompt optimization
        self.code_analyzer_model = "deepseek-ai/deepseek-coder-1.3b-instruct"    # 2.6GB - Superior code analysis
        
        # Dual model instances
        self.prompt_model = None
        self.prompt_tokenizer = None
        self.code_model = None
        self.code_tokenizer = None
        
        # Legacy single model support (fallback)
        self.model_name = "deepseek-ai/deepseek-coder-1.3b-instruct"
        self.model = None
        self.tokenizer = None
        
        # Initialize framework detector
        self.framework_detector = FrameworkDetector()
        
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        except:
            self.device = "cpu"
        self.max_length = 512
        
        # Load models on initialization
        self._load_models()
    
    def _load_models(self):

        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            print("🔧 Loading CodeLve Dual-LLM Architecture...")
            print(f"📱 Device: {self.device}")
            
            # Try to load Dual-LLM first
            try:
                # Load Prompt Engineering Model (Layer 1)
                print(f"
                self.prompt_tokenizer = AutoTokenizer.from_pretrained(self.prompt_engineer_model)
                self.prompt_model = AutoModelForCausalLM.from_pretrained(self.prompt_engineer_model)
                
                if self.prompt_tokenizer.pad_token is None:
                    self.prompt_tokenizer.pad_token = self.prompt_tokenizer.eos_token
                
                self.prompt_model.to(self.device)
                self.prompt_model.eval()
                print("✅ Prompt Engineering Layer ready!")
                
                # Load Code Analysis Model (Layer 2)
                print(f"
                self.code_tokenizer = AutoTokenizer.from_pretrained(self.code_analyzer_model)
                self.code_model = AutoModelForCausalLM.from_pretrained(self.code_analyzer_model)
                
                if self.code_tokenizer.pad_token is None:
                    self.code_tokenizer.pad_token = self.code_tokenizer.eos_token
                
                self.code_model.to(self.device)
                self.code_model.eval()
                print("✅ Code Analysis Layer ready!")
                print("🚀 Dual-LLM Architecture loaded successfully!")
                print(f"
                
            except Exception as dual_error:
                print(f"⚠️ Dual-LLM loading failed: {dual_error}")
                print("🔄 Falling back to single model...")
                
                # Fallback to single model (original implementation)
                print(f"
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
                
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                self.model.to(self.device)
                self.model.eval()
                print("✅ Code-LLM single model fallback ready!")
            
        except Exception as e:
            print(f"
            self.prompt_model = None
            self.code_model = None
            self.model = None
            self.tokenizer = None
    
    def get_status(self):

        if self.prompt_model and self.code_model:
            return {
                'architecture': 'dual-llm',
                'torch_available': True,
                'device': self.device,
                'prompt_model': self.prompt_engineer_model,
                'code_model': self.code_analyzer_model,
                'prompt_loaded': self.prompt_model is not None,
                'code_loaded': self.code_model is not None
            }
        else:
            return {
                'architecture': 'single-model',
                'torch_available': True,
                'device': self.device,
                'model_name': self.model_name,
                'model_loaded': self.model is not None
            }
    
    def check_codebase(self, query, codebase_context):

        try:
            print(f"🔄 Processing query through enhanced pipeline...")
            
            # Import analysis pipeline when needed
            from .analysis_pipeline import AnalysisPipeline
            pipeline = AnalysisPipeline(self, self.framework_detector)
            
            # PRIMARY: Use Framework-Agnostic Analysis (Proven to work)
            print("
            primary_result = pipeline.framework_agnostic_analysis_pipeline(query, codebase_context)
            
            # ENHANCEMENT: Try Dual-LLM enhancement if available (but don't rely on it)
            if self.prompt_model and self.code_model and len(primary_result) < 10000:  # Force DeepSeek to always be called
                print("🔬 Attempting Dual-LLM enhancement...")
                try:
                    enhanced_result = self._dual_llm_analysis(query, codebase_context)
                    
                    # DEBUG: Show what DeepSeek returned
                    if enhanced_result:
                        print(f"
                        print(f"
                        
                        # Only use enhanced result if it's clearly better and not just JSON
                        if (len(enhanced_result) > len(primary_result) and 
                            not enhanced_result.strip().startswith('{') and
                            not enhanced_result.strip().startswith('[') and
                            'dependencies' not in enhanced_result.lower()[:100]):
                            print("✅ Using enhanced Dual-LLM result")
                            return enhanced_result
                        else:
                            print("⚠️ Dual-LLM result not suitable, using framework-agnostic")
                            print(f"
                            return primary_result
                    else:
                        print("⚠️ No DeepSeek response received")
                        return primary_result
                        
                except Exception as e:
                    print(f"⚠️ Dual-LLM enhancement failed: {e}")
                    return primary_result
            else:
                print("✅ Using framework-agnostic primary result")
                return primary_result
                
        except Exception as e:
            return f"

    def _dual_llm_analysis(self, query, codebase_context):

        try:
            # STEP 1: PROMPT ENGINEERING LAYER
            engineered_prompt = self._engineer_prompt(query, codebase_context)
            
            # STEP 2: CODE ANALYSIS LAYER  
            if engineered_prompt:
                return self._check_with_engineered_prompt(engineered_prompt, codebase_context)
            else:
                # Fallback to framework-agnostic pipeline
                from .analysis_pipeline import AnalysisPipeline
                pipeline = AnalysisPipeline(self, self.framework_detector)
                return pipeline.framework_agnostic_analysis_pipeline(query, codebase_context)
                
        except Exception as e:
            print(f"⚠️ Dual-LLM failed: {e}, falling back to framework-agnostic analysis")
            from .analysis_pipeline import AnalysisPipeline
            pipeline = AnalysisPipeline(self, self.framework_detector)
            return pipeline.framework_agnostic_analysis_pipeline(query, codebase_context)
    
    def _engineer_prompt(self, user_query, codebase_context):

        try:
            if not self.prompt_model or not self.prompt_tokenizer:
                return self._template_prompt_fallback(user_query, codebase_context)
# FIXME: refactor when time permits
            detected_framework = self.framework_detector.detect_framework_or_language(codebase_context)
            
            # Create meta-prompt for prompt engineering
            meta_prompt = f"""Transform this user query into a detailed, technical prompt for {detected_framework} code analysis:

USER QUERY: "{user_query}"
DETECTED FRAMEWORK/LANGUAGE: {detected_framework}

Create a structured prompt that includes:
1. Analysis type (component/class/function/module/architecture)
2. Technical depth requirements for {detected_framework}
3. Business context integration
4. Framework-specific patterns and best practices
5. Output format specifications

ENGINEERED PROMPT:"""
            
            # Generate engineered prompt
            inputs = self.prompt_tokenizer.encode(
                meta_prompt, 
                return_tensors='pt', 
                max_length=self.max_length, 
                truncation=True
            )
            inputs = inputs.to(self.device)
            
            with torch.no_grad():
                outputs = self.prompt_model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 150,
                    num_return_sequences=1,
                    temperature=0.3,  # Lower temperature for consistent prompts
                    pad_token_id=self.prompt_tokenizer.eos_token_id,
                    do_sample=True
                )
            
            engineered_prompt = self.prompt_tokenizer.decode(
                outputs[0][inputs.shape[1]:], 
                skip_special_tokens=True
            ).strip()
            
            print(f"
            return engineered_prompt if engineered_prompt else self._template_prompt_fallback(user_query, codebase_context)
            
        except Exception as e:
            print(f"⚠️ Prompt engineering failed: {e}, using template fallback")
            return self._template_prompt_fallback(user_query, codebase_context)
    
    def _template_prompt_fallback(self, user_query, codebase_context):

        query_lower = user_query.lower()
        detected_framework = self.framework_detector.detect_framework_or_language(codebase_context)
        
        # INTELLIGENT ANALYSIS ROUTING with framework-aware prompts
        
        # 1. Component/Class Analysis Template
        if self._is_component_or_class_query(query_lower):
            entity_name = self._get_entity_name(user_query, detected_framework)
            return f"""Analyze the {self.framework_detector.get_entity_type(detected_framework)} '{entity_name}' with comprehensive technical depth for {detected_framework}:

1. GLOBAL CONTEXT: Explain the {self.framework_detector.get_entity_type(detected_framework)}'s role in the entire application ecosystem
2. TECHNICAL ARCHITECTURE: Break down {self.framework_detector.get_framework_specific_patterns(detected_framework)}
3. BUSINESS INTEGRATION: Connect technical implementation to business workflows
4. DEPENDENCIES: Map imports, inheritance, and data relationships
5. EXTENSIBILITY GUIDANCE: Provide specific technical modification recommendations

Focus on {detected_framework}-specific patterns and actionable insights for developers.
{self.framework_detector.get_entity_type(detected_framework)} to analyze: {entity_name}"""

        # 2. Function/Method Analysis Template
        elif self._is_function_or_method_query(query_lower):
            function_info = self._get_function_info(user_query)
            return f"""Provide deep technical analysis of the {self.framework_detector.get_function_keyword(detected_framework)} '{function_info.get('function', 'target function')}' in {detected_framework}:

1. SIGNATURE ANALYSIS: Parameters, return types, and call patterns
2. BUSINESS LOGIC FLOW: Step-by-step execution with business context
3. INTEGRATION POINTS: How this {self.framework_detector.get_function_keyword(detected_framework)} connects to other system components
4. ERROR HANDLING: Exception management and edge case coverage
5. PERFORMANCE IMPLICATIONS: Computational complexity and optimization opportunities

Deliver insights using {detected_framework} best practices and patterns."""

        # 3. Architecture Analysis Template
        elif any(word in query_lower for word in ['architecture', 'structure', 'overview', 'system']):
            return f"""Generate comprehensive {detected_framework} architecture analysis:

1. SYSTEM OVERVIEW: High-level application structure and {self.framework_detector.get_module_terminology(detected_framework)} organization
2. DATA FLOW MAPPING: How information moves between different parts of the system
3. BUSINESS DOMAIN MODELING: Core business entities and their relationships
4. INTEGRATION ARCHITECTURE: External APIs, services, and system boundaries
5. SCALABILITY ASSESSMENT: Current architecture strengths and potential bottlenecks

Provide actionable architectural insights following {detected_framework} conventions."""

        # 4. Search/Discovery Template
        elif self._is_search_query(query_lower):
            search_term = self._get_search_term(user_query)
            return f"""Execute comprehensive {detected_framework} codebase search for '{search_term}':

1. FILE DISCOVERY: Locate all files containing the search term with relevance ranking
2. FUNCTIONAL CONTEXT: Identify how the term is used across different business contexts
3. DEPENDENCY MAPPING: Show relationships between files that reference this term
4. BUSINESS IMPACT: Explain the business significance of found components
5. USAGE PATTERNS: Common {detected_framework} implementation patterns for this functionality

Deliver search results with {detected_framework}-specific context and technical depth."""

        # 5. Generic Deep Analysis Template
        else:
            return f"""Provide comprehensive {detected_framework} technical analysis for: '{user_query}'

1. TECHNICAL BREAKDOWN: Detailed analysis of relevant code components
2. BUSINESS CONTEXT: How technical implementation supports business objectives
3. SYSTEM INTEGRATION: Connections to other parts of the application
4. BEST PRACTICES: Code quality assessment using {detected_framework} standards
5. ACTIONABLE INSIGHTS: Specific guidance for {detected_framework} developers

Focus on delivering practical value for {detected_framework} software development."""
    
    def _check_with_engineered_prompt(self, engineered_prompt, codebase_context):

        try:
            if not self.code_model or not self.code_tokenizer:
                print("⚠️ Code analysis model not available, using framework-agnostic analysis")
                from .analysis_pipeline import AnalysisPipeline
                pipeline = AnalysisPipeline(self, self.framework_detector)
                return pipeline.framework_agnostic_analysis_pipeline(engineered_prompt, codebase_context)
            
            # Enhanced context selection for architecture queries
            if 'architecture' in engineered_prompt.lower():
                # For architecture queries, we need a comprehensive view
                context_lines = codebase_context.split('\n')
# Might need cleanup
                file_paths = []
                current_file = None
                for line in context_lines:
                    if line.startswith('filepath:///'):
                        file_path = line.replace('filepath:///', '').replace(' /// /// ///', '').strip()
                        file_paths.append(file_path)
                
                # Build directory tree
                import os
                
                # Create a simple directory structure
                dir_structure = "# PROJECT DIRECTORY STRUCTURE\n"
                dirs = {}
                
                for fp in file_paths[:100]:  # Analyze first 100 files for structure
                    parts = Path(fp).parts
                    for i in range(len(parts)):
                        dir_key = '/'.join(parts[:i+1])
                        dirs[dir_key] = True
                
                # Sort and format directory structure
                sorted_dirs = sorted(dirs.keys())
                prev_depth = 0
                for dir_path in sorted_dirs[:50]:  # Show top 50 directories
                    depth = dir_path.count('/')
                    indent = "  " * depth
                    name = Path(dir_path).name
                    dir_structure += f"{indent}{name}/\n"
                
                # Select representative files from different layers
                selected_files = []
                keywords = ['app', 'route', 'component', 'service', 'store', 'config', 'context', 'api', 'util']
                
                for keyword in keywords:
                    for fp in file_paths:
                        if keyword in fp.lower() and len(selected_files) < 15:
                            selected_files.append(fp)
                
                # Build smart context with selected files
                smart_context = dir_structure + "\n\n# CODEBASE CONTEXT\n"
                
                for file_path in selected_files:
                    # Find the file content in the original context
                    file_start = codebase_context.find(f"filepath:///{file_path}")
                    if file_start != -1:
                        file_end = codebase_context.find("filepath:///", file_start + 10)
                        if file_end == -1:
                            file_end = len(codebase_context)
                        
                        file_content = codebase_context[file_start:file_end]
                        # Limit each file to 1000 chars
                        if len(file_content) > 1000:
                            file_content = file_content[:1000] + "\n... (truncated)\n}\n\n"
                        smart_context += file_content
                
                # Create enhanced prompt
                full_prompt = f"""{engineered_prompt}

{smart_context}

# USER QUESTION
Explain the codebase architecture.
- Summarize the main modules/directories and their responsibilities.
- Map out major data flows (state management, API, routing, etc).
- Highlight key architectural patterns, **only if there is clear evidence in the provided code**.
- If possible, provide an ASCII or bullet diagram showing relationships between modules/components.
- **Do NOT invent or assume features that are not present in the provided files.**
- If information is incomplete or uncertain due to context truncation, clearly say so.

# CRITICAL INSTRUCTIONS
- Only refer to the code and metadata that is present in the provided context above.
- **When making claims about architecture, reference the specific files and code that prove those claims**.
- If you do not have enough evidence to answer a part of the question, say "Not enough context to determine this".

ANALYSIS:"""
            else:
                # Get smarter context - skip the header and get actual code
                context_lines = codebase_context.split('\n')
                code_start = 0
                for i, line in enumerate(context_lines):
                    if 'filepath:///' in line and not 'package.json' in line:
                        code_start = i
                        break

                # Take 1500 chars of actual code, not just package.json
                smart_context = '\n'.join(context_lines[code_start:code_start+50])

                full_prompt = f"""{engineered_prompt}

CODEBASE CONTEXT:
{smart_context}...

ANALYSIS:"""
            
            # DEBUG: Save the exact prompt sent to DeepSeek
            try:
                with open("deepseek_prompt_debug.txt", "w", encoding="utf-8") as f:
                    f.write("=== EXACT PROMPT SENT TO DEEPSEEK ===\n\n")
                    f.write(full_prompt)
                print("
            except Exception as debug_error:
                print(f"⚠️ Debug logging failed: {debug_error}")
            
            # Generate analysis
            inputs = self.code_tokenizer.encode(
                full_prompt, 
                return_tensors='pt', 
                max_length=self.max_length, 
                truncation=True
            )
            inputs = inputs.to(self.device)
            
            with torch.no_grad():
                outputs = self.code_model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 200,
                    num_return_sequences=1,
                    temperature=0.7,
                    pad_token_id=self.code_tokenizer.eos_token_id,
                    do_sample=True
                )
            
            analysis = self.code_tokenizer.decode(
                outputs[0][inputs.shape[1]:], 
                skip_special_tokens=True
            ).strip()
            
            if analysis and len(analysis) > 50:
                return f"🔬 **CodeLve Dual-LLM Analysis**\n\n{analysis}"
            else:
                # Fallback to framework-agnostic analysis if output is poor
                from .analysis_pipeline import AnalysisPipeline
                pipeline = AnalysisPipeline(self, self.framework_detector)
                return pipeline.framework_agnostic_analysis_pipeline(engineered_prompt, codebase_context)
                
        except Exception as e:
            print(f"⚠️ Code analysis failed: {e}, using framework-agnostic analysis")
            from .analysis_pipeline import AnalysisPipeline
            pipeline = AnalysisPipeline(self, self.framework_detector)
            return pipeline.framework_agnostic_analysis_pipeline(engineered_prompt, codebase_context)
    
    # QUERY TYPE DETECTION (Framework Agnostic) - Keep these in main class for template prompts
    
    def _is_component_or_class_query(self, query_lower):

        entity_indicators = ['component', 'class', 'struct', 'interface', 'module', 'service', 'controller']
        action_words = ['explain', 'analyze', 'show', 'describe', 'what is', 'how does', 'teach', 'guide']
        
        return (any(indicator in query_lower for indicator in entity_indicators) and 
                any(action in query_lower for action in action_words))
    
    def _is_function_or_method_query(self, query_lower):

        return (any(keyword in query_lower for keyword in ['function', 'method', 'func', 'def']) or 
                'from' in query_lower and any(word in query_lower for word in ['explain', 'show', 'analyze']))
    
    def _is_search_query(self, query_lower):

        search_words = ['find', 'search', 'list', 'show all', 'locate']
        return any(word in query_lower for word in search_words)
    
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
    
    def _get_search_term(self, query):

        search_words = ['find', 'search', 'list', 'show', 'all', 'locate', 'get']
        words = query.split()
        filtered_words = [word for word in words if word.lower() not in search_words]
        return ' '.join(filtered_words) if filtered_words else None
    
    def cleanup(self):

        if hasattr(self, 'prompt_model') and self.prompt_model:
            del self.prompt_model
        if hasattr(self, 'code_model') and self.code_model:
            del self.code_model
        if hasattr(self, 'prompt_tokenizer') and self.prompt_tokenizer:
            del self.prompt_tokenizer
        if hasattr(self, 'code_tokenizer') and self.code_tokenizer:
            del self.code_tokenizer
        if hasattr(self, 'model') and self.model:
            del self.model
        if hasattr(self, 'tokenizer') and self.tokenizer:
            del self.tokenizer
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print("🧹 AI client cleanup complete")