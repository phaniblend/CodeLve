"""
Dual LLM Handler - Manages DialoGPT for prompts and CodeT5+ for code generation
"""
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    T5ForConditionalGeneration,
    pipeline,
    set_seed
)
import logging
import json
import re
from typing import Dict, List, Optional, Tuple, Any
import os
import sys

# Add parent directory to path to access models folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class DualLLMHandler:
    def __init__(self):
    # Quick workaround for now
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Model paths - now correctly pointing to project root
        self.dialogpt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "dialogpt-small")
        self.codet5_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "codet5p-770m")
        
        # Initialize models
        self.dialogpt_model = None
        self.dialogpt_tokenizer = None
        self.codet5_model = None
        self.codet5_tokenizer = None
        
        # Templates for different query types
        self.prompt_templates = {
            "code_generation": {
                "template": "Generate {language} code that {task}. Consider these requirements: {requirements}. Follow these patterns: {patterns}",
                "fallback": "Write {language} code to {task}"
            },
            "explanation": {
                "template": "Explain how {component} works in this codebase. Focus on: {aspects}. Key relationships: {relationships}",
                "fallback": "Explain {component}"
            },
            "analysis": {
                "template": "Analyze {target} for {criteria}. Consider: {context}. Important factors: {factors}",
                "fallback": "Analyze {target}"
            },
            "debugging": {
                "template": "Debug {issue} in {component}. Symptoms: {symptoms}. Related code: {related_code}",
                "fallback": "Help debug {issue}"
            },
            "refactoring": {
                "template": "Refactor {code} to improve {aspects}. Maintain: {constraints}. Goals: {goals}",
                "fallback": "Refactor {code}"
            }
        }
        
    def load_models(self):

        try:
            # Load DialoGPT for prompt engineering
            logger.info(f"Loading DialoGPT from {self.dialogpt_path}")
            self.dialogpt_tokenizer = AutoTokenizer.from_pretrained(self.dialogpt_path)
            self.dialogpt_model = AutoModelForCausalLM.from_pretrained(
                self.dialogpt_path,
                torch_dtype=torch.float32
            ).to(self.device)
            
            # Add padding token if not present
            if self.dialogpt_tokenizer.pad_token is None:
                self.dialogpt_tokenizer.pad_token = self.dialogpt_tokenizer.eos_token
            
            # Load CodeT5+ for code generation
            logger.info(f"Loading CodeT5+ from {self.codet5_path}")
            self.codet5_tokenizer = AutoTokenizer.from_pretrained(self.codet5_path)
            self.codet5_model = T5ForConditionalGeneration.from_pretrained(
                self.codet5_path,
                torch_dtype=torch.float32
            ).to(self.device)
            
            logger.info("Both models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False
    
    def engineer_prompt(self, user_query: str, context: Dict[str, Any]) -> Tuple[str, str]:
        """
        Use DialoGPT to engineer better prompts for CodeT5+
        Returns: (engineered_prompt, query_type)
        """
        try:
# Works, but could be neater
            query_type = self._detect_query_type(user_query)
            
            # Create context for DialoGPT
            dialogpt_input = f"Transform this query for code AI: '{user_query}'. Context: {json.dumps(context, indent=2)}"
            
            # Generate with DialoGPT
            inputs = self.dialogpt_tokenizer.encode(dialogpt_input, return_tensors="pt", max_length=512, truncation=True)
            inputs = inputs.to(self.device)
            
            with torch.no_grad():
                outputs = self.dialogpt_model.generate(
                    inputs,
                    max_length=200,
                    num_return_sequences=1,
                    temperature=0.7,
                    pad_token_id=self.dialogpt_tokenizer.eos_token_id,
                    do_sample=True
                )
            
            engineered = self.dialogpt_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Clean up the engineered prompt
            engineered = engineered.replace(dialogpt_input, "").strip()
            
            # If DialoGPT output is too short or unclear, use template
            if len(engineered) < 20 or not self._is_valid_prompt(engineered):
                engineered = self._apply_template(user_query, query_type, context)
            
            return engineered, query_type
            
        except Exception as e:
            logger.error(f"Error in prompt engineering: {e}")
            # Fallback to template
            query_type = self._detect_query_type(user_query)
            return self._apply_template(user_query, query_type, context), query_type
    
    def generate_code(self, engineered_prompt: str, max_length: int = 512) -> str:

        try:
            # Prepare input for CodeT5+
            inputs = self.codet5_tokenizer(
                engineered_prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            ).to(self.device)
            
            # Generate code
            with torch.no_grad():
                outputs = self.codet5_model.generate(
                    **inputs,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.8,
                    do_sample=True,
                    top_p=0.95,
                    repetition_penalty=1.2
                )
            
            generated_code = self.codet5_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Post-process the generated code
            generated_code = self._post_process_code(generated_code)
            
            return generated_code
            
        except Exception as e:
            logger.error(f"Error in code generation: {e}")
            return f"# Error generating code: {str(e)}"
    
    def process_query(self, user_query: str, context: Dict[str, Any]) -> Dict[str, Any]:

        try:
            # Ensure models are loaded
            if self.dialogpt_model is None or self.codet5_model is None:
                if not self.load_models():
                    return {
                        "success": False,
                        "error": "Failed to load models",
                        "response": "Models are not available. Please check installation."
                    }
            
            # Step 1: Engineer the prompt
            engineered_prompt, query_type = self.engineer_prompt(user_query, context)
            
            # Step 2: Generate response based on query type
            if query_type in ["code_generation", "refactoring"]:
                response = self.generate_code(engineered_prompt)
                response_type = "code"
            else:
                # For non-code queries, use CodeT5+ in a different mode
                response = self._generate_explanation(engineered_prompt)
                response_type = "explanation"
            
            return {
                "success": True,
                "query_type": query_type,
                "engineered_prompt": engineered_prompt,
                "response": response,
                "response_type": response_type,
                "context_used": context
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": f"Error processing query: {str(e)}"
            }
    
    def _detect_query_type(self, query: str) -> str:

        query_lower = query.lower()
        
        if any(word in query_lower for word in ["generate", "create", "write", "build", "make"]):
            return "code_generation"
        elif any(word in query_lower for word in ["explain", "how does", "what is", "describe"]):
            return "explanation"
        elif any(word in query_lower for word in ["analyze", "review", "check", "evaluate"]):
            return "analysis"
        elif any(word in query_lower for word in ["debug", "fix", "error", "issue", "problem"]):
            return "debugging"
        elif any(word in query_lower for word in ["refactor", "improve", "optimize", "clean"]):
            return "refactoring"
        else:
            return "general"
    
    def _apply_template(self, query: str, query_type: str, context: Dict[str, Any]) -> str:

        if query_type not in self.prompt_templates:
            return query
        
        template = self.prompt_templates[query_type]["template"]
        fallback = self.prompt_templates[query_type]["fallback"]
        
        try:
# FIXME: refactor when time permits
            params = self._get_template_params(query, context, query_type)
            
            # Try to fill template
            if all(param in params for param in re.findall(r'{(\w+)}', template)):
                return template.format(**params)
            else:
                # Use fallback
                fallback_params = {k: v for k, v in params.items() if k in re.findall(r'{(\w+)}', fallback)}
                return fallback.format(**fallback_params)
                
        except:
            return query
    
    def _get_template_params(self, query: str, context: Dict[str, Any], query_type: str) -> Dict[str, str]:

        params = {}
        
        # Common extractions
        if "language" in context:
            params["language"] = context["language"]
        else:
            # Try to detect language from query
            for lang in ["python", "javascript", "java", "c++", "go", "rust"]:
                if lang in query.lower():
                    params["language"] = lang
                    break
        
        # Query-specific extractions
        if query_type == "code_generation":
            params["task"] = query
            params["requirements"] = context.get("requirements", "best practices")
            params["patterns"] = context.get("patterns", "project conventions")
            
        elif query_type == "explanation":
# Not the cleanest, but it does the job
            params["component"] = self._get_component_name(query)
            params["aspects"] = "implementation, purpose, and usage"
            params["relationships"] = context.get("relationships", "related components")
            
        # Add more query type specific extractions as needed
        
        return params
    
    def _get_component_name(self, query: str) -> str:

        # Simple extraction - can be enhanced
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ["explain", "how", "what", "describe"] and i + 1 < len(words):
                return " ".join(words[i+1:i+3])
        return "the component"
    
    def _is_valid_prompt(self, prompt: str) -> bool:

        if len(prompt) < 20:
            return False
        if prompt.count(' ') < 3:
            return False
        return True
    
    def _post_process_code(self, code: str) -> str:

        # Remove any explanation text before code
        lines = code.split('\n')
        code_started = False
        processed_lines = []
        
        for line in lines:
            if not code_started and (line.strip().startswith('def ') or 
                                    line.strip().startswith('class ') or
                                    line.strip().startswith('import ') or
                                    line.strip().startswith('from ')):
                code_started = True
            
            if code_started:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines) if processed_lines else code
    
    def _generate_explanation(self, prompt: str) -> str:

        try:
            # Modify prompt for explanation
            explanation_prompt = f"Explain: {prompt}"
            
            inputs = self.codet5_tokenizer(
                explanation_prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.codet5_model.generate(
                    **inputs,
                    max_length=256,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True
                )
            
            return self.codet5_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return f"Error generating explanation: {str(e)}"