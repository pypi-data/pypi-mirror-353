"""
Themis - AI Evaluation & Testing Framework
"""

__version__ = "0.1.2"
__author__ = "Themis Team"

# Core imports
from .core.engine import ThemisEvaluator
from .core.evaluators.hallucination import HallucinationDetector
from .core.evaluators.semantic import SemanticSimilarity
from .core.advanced.bias import BiasDetector
from .core.advanced.toxicity import ToxicityDetector

# Differential Privacy
from .core.differential_privacy.mechanisms import LaplaceMechanism, GaussianMechanism

# Testing
from .testing.framework import ABTestFramework, ModelComparison

__all__ = [
    'ThemisEvaluator',
    'HallucinationDetector',
    'SemanticSimilarity',
    'BiasDetector', 
    'ToxicityDetector',
    'LaplaceMechanism',
    'GaussianMechanism',
    'ABTestFramework',
    'ModelComparison'
]
