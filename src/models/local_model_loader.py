"""
Local Model Loader for CodeT5+
Loads models from local files instead of downloading
"""

import os
import torch
from transformers import (
    T5ForConditionalGeneration, 
    AutoTokenizer,
    AutoModelForCausalLM
)
from pathlib import Path
import logging
from typing import Tuple, Optional


class LocalModelLoader:
    """Load CodeT5+ from local files"""
    
    def __init__(self, models_dir: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Set models directory
        if models_dir:
            self.models_dir = Path(models_dir)
        else:
            # Default to models folder relative to project root
            self.models_dir = Path(__file__).parent.parent.parent / "models"
        
        # Model paths
        self.codet5_path = self.models_dir / "codet5p-770m"
        self.dialogpt_path = self.models_dir / "dialogpt-small"
        
        # Verify paths exist
        self._verify_model_files()
    
    def _verify_model_files(self):
        """Verify all required model files exist"""
        required_files = {
            "codet5p-770m": [
                "pytorch_model.bin",
                "config.json",
                "tokenizer_config.json",
                "special_tokens_map.json"
            ]
        }
        
        for model_name, files in required_files.items():
            model_path = self.models_dir / model_name
            if not model_path.exists():
                self.logger.warning(f"Model directory not found: {model_path}")
                continue
                
            for file in files:
                file_path = model_path / file
                if not file_path.exists():
                    self.logger.warning(f"Missing file: {file_path}")
                else:
                    self.logger.info(f"✓ Found: {file}")
    
    def load_codet5_model(self) -> Tuple[T5ForConditionalGeneration, AutoTokenizer]:
        """Load CodeT5+ model from local files"""
        try:
            self.logger.info(f"Loading CodeT5+ from {self.codet5_path}")
            
            # Use AutoTokenizer to automatically detect the correct tokenizer type
            tokenizer = AutoTokenizer.from_pretrained(
                str(self.codet5_path),
                local_files_only=True,
                trust_remote_code=True
            )
            
            # Load model from local files
            model = T5ForConditionalGeneration.from_pretrained(
                str(self.codet5_path),
                local_files_only=True,
                torch_dtype=torch.float32  # Use float32 for CPU
            )
            
            # Move to CPU and optimize
            model = model.to('cpu')
            model.eval()  # Set to evaluation mode
            
            # Set decoder_start_token_id if not set
            if model.config.decoder_start_token_id is None:
                model.config.decoder_start_token_id = tokenizer.pad_token_id
            
            self.logger.info("✅ CodeT5+ loaded successfully!")
            self.logger.info(f"Tokenizer type: {type(tokenizer).__name__}")
            return model, tokenizer
            
        except Exception as e:
            self.logger.error(f"Failed to load CodeT5+: {str(e)}")
            raise
    
    def load_dialogpt_model(self) -> Optional[Tuple]:
        """Load DialoGPT model (download if needed)"""
        try:
            # First try local
            if self.dialogpt_path.exists():
                self.logger.info(f"Loading DialoGPT from {self.dialogpt_path}")
                tokenizer = AutoTokenizer.from_pretrained(
                    str(self.dialogpt_path),
                    local_files_only=True
                )
                model = AutoModelForCausalLM.from_pretrained(
                    str(self.dialogpt_path),
                    local_files_only=True,
                    torch_dtype=torch.float32
                )
            else:
                # Download if not exists
                self.logger.info("DialoGPT not found locally, downloading...")
                model_name = "microsoft/DialoGPT-small"
                
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float32
                )
                
                # Save for future use
                self.save_dialogpt_model(model, tokenizer)
            
            # Optimize for CPU
            model = model.to('cpu')
            model.eval()
            
            # Add padding token
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            self.logger.info("✅ DialoGPT loaded successfully!")
            return model, tokenizer
            
        except Exception as e:
            self.logger.error(f"Failed to load DialoGPT: {str(e)}")
            return None
    
    def save_dialogpt_model(self, model, tokenizer):
        """Save DialoGPT locally for future use"""
        try:
            self.dialogpt_path.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(str(self.dialogpt_path))
            tokenizer.save_pretrained(str(self.dialogpt_path))
            self.logger.info(f"DialoGPT saved to {self.dialogpt_path}")
        except Exception as e:
            self.logger.warning(f"Could not save DialoGPT: {e}")
    
    def get_model_info(self):
        """Get information about available models"""
        info = {
            "models_directory": str(self.models_dir),
            "codet5_available": self.codet5_path.exists(),
            "dialogpt_available": self.dialogpt_path.exists()
        }
        
        # Add file sizes
        if self.codet5_path.exists():
            model_file = self.codet5_path / "pytorch_model.bin"
            if model_file.exists():
                size_mb = model_file.stat().st_size / (1024 * 1024)
                info["codet5_size_mb"] = f"{size_mb:.1f}"
        
        return info


# Convenience function for testing
def test_local_loader():
    """Test the local model loader"""
    logging.basicConfig(level=logging.INFO)
    
    loader = LocalModelLoader()
    print("\nModel Info:", loader.get_model_info())
    
    # Test loading CodeT5+
    try:
        model, tokenizer = loader.load_codet5_model()
        print("\n✅ CodeT5+ loaded successfully!")
        print(f"Model type: {type(model).__name__}")
        print(f"Tokenizer type: {type(tokenizer).__name__}")
        
        # Test inference with proper prompting for CodeT5+
        input_text = "def fibonacci(n):"
        task_prefix = "complete: "  # CodeT5+ task prefix
        
        inputs = tokenizer(
            task_prefix + input_text, 
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
        
        print(f"\nTest input: {input_text}")
        print("Generating code completion...")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_length=100,
                num_beams=5,
                early_stopping=True,
                temperature=0.2
            )
            result = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"Generated: {result}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_local_loader()