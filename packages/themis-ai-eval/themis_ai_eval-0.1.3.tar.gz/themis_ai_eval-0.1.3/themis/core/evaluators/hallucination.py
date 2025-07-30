"""
Hallucination detection evaluator.
"""

import re
from typing import Any, Dict, List, Optional
from .base import TextEvaluator


class HallucinationDetector(TextEvaluator):
    """Detect hallucinations in model outputs."""
    
    def evaluate(self, model_outputs: List[str], 
                ground_truth: Optional[List[str]] = None,
                contexts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Evaluate hallucination."""
        
        if not model_outputs:
            return {'hallucination_rate': 0.0, 'total_outputs': 0}
        
        total_outputs = len(model_outputs)
        hallucination_count = 0
        
        for i, output in enumerate(model_outputs):
            # Simple hallucination detection heuristics
            if self._detect_hallucination(output, ground_truth[i] if ground_truth else None):
                hallucination_count += 1
        
        hallucination_rate = hallucination_count / total_outputs
        
        return {
            'hallucination_rate': hallucination_rate,
            'hallucination_count': hallucination_count,
            'total_outputs': total_outputs,
            'accuracy': 1.0 - hallucination_rate
        }
    
    def _detect_hallucination(self, output: str, ground_truth: Optional[str] = None) -> bool:
        """Simple hallucination detection."""
        
        # Check for obvious false statements
        false_patterns = [
            r'the earth is flat',
            r'the moon is made of cheese',
            r'gravity does not exist',
            r'vaccines cause autism',
            r'climate change is fake'
        ]
        
        output_lower = output.lower()
        for pattern in false_patterns:
            if re.search(pattern, output_lower):
                return True
        
        # If ground truth provided, check similarity
        if ground_truth:
            output_words = set(self.normalize_text(output).split())
            truth_words = set(self.normalize_text(ground_truth).split())
            
            if output_words and truth_words:
                overlap = len(output_words.intersection(truth_words))
                similarity = overlap / len(output_words.union(truth_words))
                
                # Consider low similarity as potential hallucination
                return similarity < 0.3
        
        return False
