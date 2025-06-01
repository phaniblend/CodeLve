"""
CodeLve AI Client Package
Enhanced HuggingFace AI client with Dual-LLM Prompt Engineering Layer + Framework-Agnostic Analysis
"""

from .hf_ai_client import HuggingFaceAIClient
from .framework_detector import FrameworkDetector
from .analysis_pipeline import AnalysisPipeline
from .technical_analyzers import TechnicalAnalyzers
from .architecture_analyzer import ArchitectureAnalyzer
from .entity_analyzer import EntityAnalyzer
from .search_utilities import SearchUtilities

__version__ = "1.0.0"
__author__ = "CodeLve Team"

__all__ = [
    'HuggingFaceAIClient',
    'FrameworkDetector', 
    'AnalysisPipeline',
    'TechnicalAnalyzers',
    'ArchitectureAnalyzer',
    'EntityAnalyzer',
    'SearchUtilities'
]