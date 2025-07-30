"""
Base evaluator classes.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseEvaluator(ABC):
    """Base class for all evaluators."""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def evaluate(self, model_outputs: List[str], 
                ground_truth: Optional[List[str]] = None,
                contexts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Evaluate model outputs."""
        pass


class TextEvaluator(BaseEvaluator):
    """Base class for text evaluators."""
    
    def normalize_text(self, text: str) -> str:
        """Normalize text."""
        return text.lower().strip()
