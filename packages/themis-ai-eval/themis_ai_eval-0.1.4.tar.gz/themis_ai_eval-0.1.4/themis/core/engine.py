"""
Core evaluation engine.
"""

import uuid
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class EvaluationResult:
    """Container for evaluation results."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    evaluator_name: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'evaluator_name': self.evaluator_name,
            'metrics': self.metrics,
            'execution_time': self.execution_time,
            'success': self.success
        }


@dataclass
class EvaluationSuite:
    """Container for multiple evaluation results."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    results: List[EvaluationResult] = field(default_factory=list)
    
    def add_result(self, result: EvaluationResult):
        self.results.append(result)
    
    def summary(self) -> Dict[str, Any]:
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        
        return {
            'total_evaluations': total,
            'successful_evaluations': successful,
            'success_rate': successful / total if total > 0 else 0.0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'results': [r.to_dict() for r in self.results],
            'summary': self.summary()
        }


class ThemisEvaluator:
    """Main evaluation engine."""
    
    def __init__(self):
        self.evaluators = {}
    
    def add_evaluator(self, evaluator, name: Optional[str] = None):
        """Add an evaluator."""
        evaluator_name = name or evaluator.__class__.__name__
        self.evaluators[evaluator_name] = evaluator
        print(f"Added evaluator: {evaluator_name}")
    
    def evaluate(self, model_outputs: List[str], 
                ground_truth: Optional[List[str]] = None,
                contexts: Optional[List[str]] = None) -> EvaluationSuite:
        """Run evaluation."""
        suite = EvaluationSuite()
        
        for name, evaluator in self.evaluators.items():
            try:
                start_time = time.time()
                
                metrics = evaluator.evaluate(
                    model_outputs=model_outputs,
                    ground_truth=ground_truth,
                    contexts=contexts
                )
                
                execution_time = time.time() - start_time
                
                result = EvaluationResult(
                    evaluator_name=name,
                    metrics=metrics,
                    execution_time=execution_time,
                    success=True
                )
                
                suite.add_result(result)
                
            except Exception as e:
                result = EvaluationResult(
                    evaluator_name=name,
                    success=False,
                    error_message=str(e)
                )
                suite.add_result(result)
        
        return suite
