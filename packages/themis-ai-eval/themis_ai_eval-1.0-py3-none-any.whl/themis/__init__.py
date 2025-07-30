"""
Themis - AI Evaluation & Testing Framework
"""

__version__ = "0.1.2"  # Increment version
__author__ = "Themis Team"

# Core imports (required)
try:
    from .core.engine import ThemisEvaluator, EvaluationResult, EvaluationSuite
except ImportError as e:
    print(f"Warning: Could not import core components: {e}")
    ThemisEvaluator = EvaluationResult = EvaluationSuite = None

# Evaluator imports (required)
try:
    from .core.evaluators.hallucination import HallucinationDetector
except ImportError as e:
    print(f"Warning: Could not import HallucinationDetector: {e}")
    HallucinationDetector = None

try:
    from .core.evaluators.semantic import SemanticSimilarity
except ImportError as e:
    print(f"Warning: Could not import SemanticSimilarity: {e}")
    SemanticSimilarity = None

try:
    from .core.advanced.bias import BiasDetector
except ImportError as e:
    print(f"Warning: Could not import BiasDetector: {e}")
    BiasDetector = None

try:
    from .core.advanced.toxicity import ToxicityDetector
except ImportError as e:
    print(f"Warning: Could not import ToxicityDetector: {e}")
    ToxicityDetector = None

# Differential Privacy imports (optional)
try:
    from .core.differential_privacy.mechanisms import LaplaceMechanism, GaussianMechanism
except ImportError as e:
    print(f"Warning: Could not import differential privacy mechanisms: {e}")
    LaplaceMechanism = GaussianMechanism = None

# Testing framework imports (optional)
try:
    from .testing.framework import ABTestFramework, ModelComparison
except ImportError as e:
    print(f"Warning: Could not import testing framework: {e}")
    ABTestFramework = ModelComparison = None

# Define what gets imported with "from themis import *"
__all__ = [
    'ThemisEvaluator',
    'EvaluationResult',
    'EvaluationSuite',
    'HallucinationDetector',
    'SemanticSimilarity',
    'BiasDetector', 
    'ToxicityDetector',
    'LaplaceMechanism',
    'GaussianMechanism',
    'ABTestFramework',
    'ModelComparison'
]

# Remove None values from __all__
__all__ = [name for name in __all__ if globals().get(name) is not None]
