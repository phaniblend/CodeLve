"""
Dual LLM Handler for CodeLve
Manages the dual-LLM architecture for enhanced code analysis
"""

import os
import json
from typing import Optional, Dict, Any

class DualLLMHandler:
    """Handle dual-LLM prompt engineering and enhancement using LOCAL models"""
    
    def __init__(self, ai_client=None):
        # Use local models from HuggingFaceAIClient
        self.ai_client = ai_client
        
        # No API keys needed - everything is local!
        print("🚀 DualLLMHandler initialized with local models")
    
    def enhance_response(self, prompt: str, context: str, framework: str = None) -> Optional[str]:
        """Enhance response using LOCAL DeepSeek model"""
        if not self.ai_client:
            print("⚠️ No AI client available for enhancement")
            return None
            
        if not hasattr(self.ai_client, 'code_model') or not self.ai_client.code_model:
            print("⚠️ Local code model not loaded")
            return None
        
        try:
            # Create the enhanced prompt
            system_prompt = self._create_system_prompt(framework)
            
            # Prepare the full prompt
            full_prompt = f"{system_prompt}\n\nUser Query: {prompt}\n\nAnalysis:"
            
            print("🎯 Using local DeepSeek model for enhancement...")
            
            # Use LOCAL model for generation
            import torch
            inputs = self.ai_client.code_tokenizer.encode(
                full_prompt, 
                return_tensors='pt', 
                max_length=self.ai_client.max_length, 
                truncation=True
            )
            inputs = inputs.to(self.ai_client.device)
            
            with torch.no_grad():
                outputs = self.ai_client.code_model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 300,
                    num_return_sequences=1,
                    temperature=0.7,
                    pad_token_id=self.ai_client.code_tokenizer.eos_token_id,
                    do_sample=True
                )
            
            enhanced_response = self.ai_client.code_tokenizer.decode(
                outputs[0][inputs.shape[1]:], 
                skip_special_tokens=True
            ).strip()
            
            print(f"✅ Local DeepSeek response received: {len(enhanced_response)} chars")
            
            # Validate the response
            if self._is_valid_enhancement(enhanced_response, prompt):
                return enhanced_response
            else:
                print("⚠️ Enhancement validation failed")
                return None
                
        except Exception as e:
            print(f"❌ Error enhancing response: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_system_prompt(self, framework: str) -> str:
        """Create system prompt based on framework"""
        base_prompt = """You are CodeLve, an expert code analysis assistant. 
Your role is to provide detailed, actionable insights about codebases.
Focus on practical, developer-friendly explanations."""
        
        if framework and 'React' in framework:
            return base_prompt + """
You specialize in React/TypeScript applications.
When analyzing components, focus on:
- Props and state management
- Hooks usage and lifecycle
- Component composition and reusability
- Performance considerations
- Testing strategies"""
        
        elif framework and 'Python' in framework:
            return base_prompt + """
You specialize in Python applications.
When analyzing code, focus on:
- Class and function design
- Module organization
- Error handling patterns
- Performance optimization
- Testing approaches"""
        
        return base_prompt
    
    def _is_valid_enhancement(self, response: str, original_prompt: str) -> bool:
        """Validate that the enhancement is appropriate"""
        # Basic validation
        if not response or len(response) < 100:
            return False
        
        # Check if it's not just an error message
        error_indicators = ['sorry', 'cannot', 'error', 'invalid']
        if any(indicator in response.lower()[:100] for indicator in error_indicators):
            return False
        
        # Check if it's relevant to code analysis
        code_indicators = ['component', 'function', 'code', 'implementation', 'class', 'method']
        if not any(indicator in response.lower() for indicator in code_indicators):
            return False
        
        return True
    
    def engineer_prompt(self, user_query: str, analysis_type: str, context: Dict[str, Any]) -> str:
        """Engineer an optimized prompt based on query type"""
        
        if analysis_type == 'architecture':
            return self._engineer_architecture_prompt(user_query, context)
        elif analysis_type == 'entity':
            return self._engineer_entity_prompt(user_query, context)
        elif analysis_type == 'search':
            return self._engineer_search_prompt(user_query, context)
        else:
            return user_query
    
    def _engineer_architecture_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Engineer prompt for architecture analysis"""
        framework = context.get('framework', 'Unknown')
        stats = context.get('stats', {})
        
        return f"""Analyze the architecture of this {framework} application.

Project Statistics:
- Files: {stats.get('files', 'N/A')}
- Lines: {stats.get('lines', 'N/A')}
- Framework: {framework}

User Question: {query}

Provide a comprehensive architectural analysis including:
1. Overall system design and structure
2. Key architectural patterns and decisions
3. Module organization and dependencies
4. Data flow and component interactions
5. Strengths and potential improvements
6. Specific recommendations for the development team

Focus on practical insights that help developers understand and work with this codebase."""
    
    def _engineer_entity_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Engineer prompt for entity analysis"""
        entity_name = context.get('entity_name', 'component')
        entity_type = context.get('entity_type', 'code')
        
        return f"""Analyze the {entity_type} named '{entity_name}'.

User Question: {query}

Provide detailed analysis including:
1. Purpose and responsibility
2. Implementation details
3. Dependencies and interactions
4. Usage patterns
5. Potential issues or improvements
6. Testing considerations

Make the explanation clear and actionable for developers."""
    
    def _engineer_search_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Engineer prompt for search queries"""
        search_term = context.get('search_term', '')
        
        return f"""Help find information about '{search_term}' in the codebase.

User Question: {query}

Provide:
1. Where this term appears in the codebase
2. Its purpose and usage
3. Related components or concepts
4. Examples of how it's used
5. Best practices for working with it"""