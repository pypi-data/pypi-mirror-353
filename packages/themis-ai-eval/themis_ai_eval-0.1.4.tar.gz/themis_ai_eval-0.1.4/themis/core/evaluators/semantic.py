"""
Semantic similarity evaluator.
"""

from typing import Any, Dict, List, Optional
from .base import TextEvaluator


class SemanticSimilarity(TextEvaluator):
    """Measure semantic similarity."""
    
    def evaluate(self, model_outputs: List[str], 
                ground_truth: Optional[List[str]] = None,
                contexts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Evaluate semantic similarity."""
        
        if not ground_truth:
            return {'error': 'Ground truth required for semantic similarity'}
        
        similarities = []
        
        for output, truth in zip(model_outputs, ground_truth):
            similarity = self._compute_similarity(output, truth)
            similarities.append(similarity)
        
        if similarities:
            mean_similarity = sum(similarities) / len(similarities)
            max_similarity = max(similarities)
            min_similarity = min(similarities)
        else:
            mean_similarity = max_similarity = min_similarity = 0.0
        
        return {
            'mean_similarity': mean_similarity,
            'max_similarity': max_similarity,
            'min_similarity': min_similarity,
            'similarities': similarities
        }
    
    def _compute_similarity(self, text1: str, text2: str) -> float:
        """Compute similarity using simple token overlap."""
        tokens1 = set(self.normalize_text(text1).split())
        tokens2 = set(self.normalize_text(text2).split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union)  # Jaccard similarity
