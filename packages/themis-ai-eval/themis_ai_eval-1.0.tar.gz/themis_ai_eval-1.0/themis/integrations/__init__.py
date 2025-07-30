"""Integration modules."""
# Integrations are optional and may not be fully implemented
try:
    from .huggingface import HuggingFaceIntegration
except ImportError:
    HuggingFaceIntegration = None

try:
    from .openai import OpenAIIntegration
except ImportError:
    OpenAIIntegration = None

try:
    from .fastapi import FastAPIIntegration
except ImportError:
    FastAPIIntegration = None

try:
    from .mlflow import MLflowIntegration
except ImportError:
    MLflowIntegration = None

__all__ = ['HuggingFaceIntegration', 'OpenAIIntegration', 'FastAPIIntegration', 'MLflowIntegration']
