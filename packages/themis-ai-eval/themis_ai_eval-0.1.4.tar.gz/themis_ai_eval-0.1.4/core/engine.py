"""
Core evaluation engine that orchestrates evaluators and processes results.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid

from ..utils.metrics import MetricsCalculator
from ..analytics.processor import ResultsProcessor


@dataclass
class EvaluationResult:
    """Container for evaluation results."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    evaluator_name: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'evaluator_name': self.evaluator_name,
            'metrics': self.metrics,
            'metadata': self.metadata,
            'execution_time': self.execution_time,
            'success': self.success,
            'error_message': self.error_message
        }


@dataclass
class EvaluationSuite:
    """Container for multiple evaluation results."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    results: List[EvaluationResult] = field(default_factory=list)
    summary_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_result(self, result: EvaluationResult) -> None:
        """Add evaluation result to suite."""
        self.results.append(result)
    
    def get_results_by_evaluator(self, evaluator_name: str) -> List[EvaluationResult]:
        """Get results for specific evaluator."""
        return [r for r in self.results if r.evaluator_name == evaluator_name]
    
    def summary(self) -> Dict[str, Any]:
        """Generate summary of evaluation suite."""
        total_evaluations = len(self.results)
        successful_evaluations = sum(1 for r in self.results if r.success)
        failed_evaluations = total_evaluations - successful_evaluations
        
        avg_execution_time = (
            sum(r.execution_time for r in self.results) / total_evaluations
            if total_evaluations > 0 else 0.0
        )
        
        return {
            'suite_id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'total_evaluations': total_evaluations,
            'successful_evaluations': successful_evaluations,
            'failed_evaluations': failed_evaluations,
            'success_rate': successful_evaluations / total_evaluations if total_evaluations > 0 else 0.0,
            'average_execution_time': avg_execution_time,
            'evaluators_used': list(set(r.evaluator_name for r in self.results)),
            'summary_metrics': self.summary_metrics
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'results': [r.to_dict() for r in self.results],
            'summary_metrics': self.summary_metrics,
            'metadata': self.metadata,
            'summary': self.summary()
        }


class ThemisEvaluator:
    """
    Main evaluation engine that orchestrates evaluators and processes results.
    """
    
    def __init__(
        self,
        max_workers: int = 4,
        timeout: float = 300.0,
        enable_async: bool = True,
        cache_results: bool = True
    ):
        """
        Initialize ThemisEvaluator.
        
        Args:
            max_workers: Maximum number of worker threads
            timeout: Timeout for individual evaluations in seconds
            enable_async: Enable asynchronous evaluation
            cache_results: Enable result caching
        """
        self.evaluators: Dict[str, Any] = {}
        self.max_workers = max_workers
        self.timeout = timeout
        self.enable_async = enable_async
        self.cache_results = cache_results
        self._cache: Dict[str, EvaluationResult] = {}
        
        # Initialize components
        self.metrics_calculator = MetricsCalculator()
        self.results_processor = ResultsProcessor()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def add_evaluator(
        self, 
        evaluator: Any, 
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an evaluator to the evaluation suite.
        
        Args:
            evaluator: Evaluator instance
            name: Optional name for the evaluator
            config: Optional configuration for the evaluator
        """
        evaluator_name = name or evaluator.__class__.__name__
        
        # Store evaluator with configuration
        self.evaluators[evaluator_name] = {
            'instance': evaluator,
            'config': config or {},
            'enabled': True
        }
        
        self.logger.info(f"Added evaluator: {evaluator_name}")
    
    def remove_evaluator(self, name: str) -> None:
        """Remove an evaluator."""
        if name in self.evaluators:
            del self.evaluators[name]
            self.logger.info(f"Removed evaluator: {name}")
    
    def list_evaluators(self) -> List[str]:
        """List all registered evaluators."""
        return list(self.evaluators.keys())
    
    def enable_evaluator(self, name: str) -> None:
        """Enable a specific evaluator."""
        if name in self.evaluators:
            self.evaluators[name]['enabled'] = True
    
    def disable_evaluator(self, name: str) -> None:
        """Disable a specific evaluator."""
        if name in self.evaluators:
            self.evaluators[name]['enabled'] = False
    
    def evaluate(
        self,
        model_outputs: Union[str, List[str]],
        ground_truth: Optional[Union[str, List[str]]] = None,
        contexts: Optional[Union[str, List[str]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        evaluators: Optional[List[str]] = None
    ) -> EvaluationSuite:
        """
        Run evaluation on model outputs.
        
        Args:
            model_outputs: Model outputs to evaluate
            ground_truth: Ground truth for comparison
            contexts: Context information
            metadata: Additional metadata
            evaluators: Specific evaluators to run (if None, runs all enabled)
        
        Returns:
            EvaluationSuite containing all results
        """
        # Normalize inputs to lists
        if isinstance(model_outputs, str):
            model_outputs = [model_outputs]
        if isinstance(ground_truth, str):
            ground_truth = [ground_truth]
        if isinstance(contexts, str):
            contexts = [contexts]
        
        # Create evaluation suite
        suite = EvaluationSuite(metadata=metadata or {})
        
        # Determine which evaluators to run
        target_evaluators = evaluators or [
            name for name, config in self.evaluators.items() 
            if config['enabled']
        ]
        
        if self.enable_async:
            results = self._evaluate_async(
                model_outputs, ground_truth, contexts, target_evaluators
            )
        else:
            results = self._evaluate_sync(
                model_outputs, ground_truth, contexts, target_evaluators
            )
        
        # Add results to suite
        for result in results:
            suite.add_result(result)
        
        # Calculate summary metrics
        suite.summary_metrics = self._calculate_summary_metrics(suite)
        
        return suite
    
    def _evaluate_sync(
        self,
        model_outputs: List[str],
        ground_truth: Optional[List[str]],
        contexts: Optional[List[str]],
        evaluators: List[str]
    ) -> List[EvaluationResult]:
        """Synchronous evaluation."""
        results = []
        
        for evaluator_name in evaluators:
            if evaluator_name not in self.evaluators:
                continue
                
            evaluator_config = self.evaluators[evaluator_name]
            evaluator = evaluator_config['instance']
            
            try:
                start_time = datetime.now()
                
                # Run evaluator
                metrics = evaluator.evaluate(
                    model_outputs=model_outputs,
                    ground_truth=ground_truth,
                    contexts=contexts,
                    **evaluator_config['config']
                )
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                result = EvaluationResult(
                    evaluator_name=evaluator_name,
                    metrics=metrics,
                    execution_time=execution_time,
                    success=True
                )
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error in evaluator {evaluator_name}: {str(e)}")
                result = EvaluationResult(
                    evaluator_name=evaluator_name,
                    success=False,
                    error_message=str(e)
                )
                results.append(result)
        
        return results
    
    def _evaluate_async(
        self,
        model_outputs: List[str],
        ground_truth: Optional[List[str]],
        contexts: Optional[List[str]],
        evaluators: List[str]
    ) -> List[EvaluationResult]:
        """Asynchronous evaluation using thread pool."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all evaluation tasks
            future_to_evaluator = {}
            
            for evaluator_name in evaluators:
                if evaluator_name not in self.evaluators:
                    continue
                    
                future = executor.submit(
                    self._run_single_evaluator,
                    evaluator_name,
                    model_outputs,
                    ground_truth,
                    contexts
                )
                future_to_evaluator[future] = evaluator_name
            
            # Collect results as they complete
            for future in as_completed(future_to_evaluator, timeout=self.timeout):
                evaluator_name = future_to_evaluator[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error in evaluator {evaluator_name}: {str(e)}")
                    result = EvaluationResult(
                        evaluator_name=evaluator_name,
                        success=False,
                        error_message=str(e)
                    )
                    results.append(result)
        
        return results
    
    def _run_single_evaluator(
        self,
        evaluator_name: str,
        model_outputs: List[str],
        ground_truth: Optional[List[str]],
        contexts: Optional[List[str]]
    ) -> EvaluationResult:
        """Run a single evaluator."""
        evaluator_config = self.evaluators[evaluator_name]
        evaluator = evaluator_config['instance']
        
        start_time = datetime.now()
        
        # Check cache if enabled
        cache_key = self._generate_cache_key(
            evaluator_name, model_outputs, ground_truth, contexts
        )
        
        if self.cache_results and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Run evaluator
        metrics = evaluator.evaluate(
            model_outputs=model_outputs,
            ground_truth=ground_truth,
            contexts=contexts,
            **evaluator_config['config']
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        result = EvaluationResult(
            evaluator_name=evaluator_name,
            metrics=metrics,
            execution_time=execution_time,
            success=True
        )
        
        # Cache result if enabled
        if self.cache_results:
            self._cache[cache_key] = result
        
        return result
    
    def _generate_cache_key(
        self,
        evaluator_name: str,
        model_outputs: List[str],
        ground_truth: Optional[List[str]],
        contexts: Optional[List[str]]
    ) -> str:
        """Generate cache key for evaluation."""
        import hashlib
        
        content = {
            'evaluator': evaluator_name,
            'outputs': model_outputs,
            'truth': ground_truth,
            'contexts': contexts
        }
        
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _calculate_summary_metrics(self, suite: EvaluationSuite) -> Dict[str, Any]:
        """Calculate summary metrics for the evaluation suite."""
        summary = {}
        
        # Aggregate metrics by type
        metric_aggregations = {}
        
        for result in suite.results:
            if not result.success:
                continue
                
            for metric_name, metric_value in result.metrics.items():
                if metric_name not in metric_aggregations:
                    metric_aggregations[metric_name] = []
                metric_aggregations[metric_name].append(metric_value)
        
        # Calculate statistics for each metric
        for metric_name, values in metric_aggregations.items():
            if not values:
                continue
                
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            
            if numeric_values:
                summary[f"{metric_name}_mean"] = sum(numeric_values) / len(numeric_values)
                summary[f"{metric_name}_min"] = min(numeric_values)
                summary[f"{metric_name}_max"] = max(numeric_values)
                
                if len(numeric_values) > 1:
                    variance = sum((x - summary[f"{metric_name}_mean"]) ** 2 for x in numeric_values) / len(numeric_values)
                    summary[f"{metric_name}_std"] = variance ** 0.5
        
        return summary
    
    def clear_cache(self) -> None:
        """Clear evaluation cache."""
        self._cache.clear()
        self.logger.info("Evaluation cache cleared")
    
    def get_cache_size(self) -> int:
        """Get current cache size."""
        return len(self._cache)