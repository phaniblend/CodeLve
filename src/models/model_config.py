"""
Model Configuration for CodeLve
Using CodeT5+ for superior code analysis and generation
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ModelConfig:

    
    # Prompt Engineering Model - Enhances user queries
    PROMPT_MODEL = {
        "name": "microsoft/DialoGPT-small",
        "size_mb": 117,
        "type": "conversational",
        "purpose": "Query understanding and enhancement",
        "max_length": 512,
        "temperature": 0.7
    }
    
    # Code Analysis & Generation Model - The powerhouse
    CODE_MODEL = {
        "name": "Salesforce/codet5p-770m",
        "size_mb": 770,
        "type": "encoder-decoder",
        "purpose": "Code analysis, generation, and bug detection",
        "max_length": 512,
        "max_new_tokens": 256,
        "temperature": 0.2,  # Lower for more deterministic code generation
        "supported_tasks": [
            "code_generation",
            "code_completion", 
            "code_summarization",
            "bug_detection",
            "code_translation"
        ]
    }
    
    # Total download size
    TOTAL_SIZE_MB = PROMPT_MODEL["size_mb"] + CODE_MODEL["size_mb"]  # 887MB
    
    # CPU Optimization Settings
    CPU_SETTINGS = {
        "num_threads": 8,  # Adjust based on CPU cores
        "use_half_precision": False,  # Keep False for CPU (True for GPU)
        "batch_size": 1,
        "use_cache": True,
        "max_cache_size": 1000  # Cache recent queries
    }
    
    # Task-specific prompts for CodeT5+
    TASK_PROMPTS = {
        "generate": "Generate code: ",
        "analyze": "Analyze code: ",
        "fix_bug": "Fix bug in code: ",
        "explain": "Explain code: ",
        "complete": "Complete code: ",
        "summarize": "Summarize code: "
    }
    
    @classmethod
    def get_model_config(cls, model_type: str) -> Dict[str, Any]:
    # Not the cleanest, but it does the job

        if model_type == "prompt":
            return cls.PROMPT_MODEL
        elif model_type == "code":
            return cls.CODE_MODEL
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    @classmethod
    def get_generation_config(cls, task: str = "generate") -> Dict[str, Any]:

        base_config = {
            "max_new_tokens": 256,
            "temperature": 0.2,
            "top_p": 0.95,
            "do_sample": True,
            "pad_token_id": 0,
            "eos_token_id": 2
        }
        
        # Task-specific adjustments
        if task == "fix_bug":
            base_config["temperature"] = 0.1  # More deterministic for bug fixes
        elif task == "generate":
            base_config["max_new_tokens"] = 512  # Longer for full component generation
        elif task == "explain":
            base_config["temperature"] = 0.5  # More creative for explanations
            
        return base_config
    
    @classmethod
    def format_prompt_for_task(cls, task: str, content: str) -> str:

        task_prefix = cls.TASK_PROMPTS.get(task, "")
        return f"{task_prefix}{content}"