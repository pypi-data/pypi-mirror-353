# Themis - AI Evaluation & Testing Framework

🏛️ **Themis** is a comprehensive Python library for evaluating and testing AI systems, with a focus on LLM outputs, bias detection, hallucination measurement, and differential privacy.

[![PyPI version](https://badge.fury.io/py/themis-ai-eval.svg)](https://badge.fury.io/py/themis-ai-eval)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/themis-ai/themis/workflows/tests/badge.svg)](https://github.com/themis-ai/themis/actions)

## Features

### 🔍 Core Evaluators
- **Hallucination Detection**: Measure factual accuracy and consistency
- **Semantic Similarity**: Compare meaning across model outputs
- **Performance Metrics**: Latency, throughput, and resource usage
- **Robustness Testing**: Adversarial and edge case evaluation

### 🧠 Advanced Evaluators  
- **Bias Detection**: Identify and measure various forms of bias
- **Toxicity Detection**: Content safety and harmful output detection
- **Factual Accuracy**: Cross-reference with knowledge bases
- **Coherence Analysis**: Logical consistency and flow evaluation

### 🔒 Differential Privacy
- **Privacy Mechanisms**: Laplace, Gaussian, and exponential mechanisms
- **Privacy Metrics**: Epsilon-delta privacy analysis
- **Utility-Privacy Tradeoffs**: Measure privacy cost vs. model utility

### 🧪 A/B Testing Framework
- **Model Comparison**: Statistical significance testing
- **Performance Benchmarking**: Standardized evaluation protocols
- **Regression Detection**: Identify performance degradations

### 🔗 Integrations
- **Hugging Face**: Direct model evaluation from Hub
- **OpenAI**: GPT model testing and evaluation
- **FastAPI**: RESTful evaluation endpoints
- **MLflow**: Experiment tracking and model versioning

## Installation

```bash
# Basic installation
pip install themis-ai-eval

# With all dependencies
pip install themis-ai-eval[all]

# Development installation
pip install themis-ai-eval[dev]
```

## Quick Start

### Basic Evaluation

```python
from themis import ThemisEvaluator
from themis.core.evaluators import HallucinationDetector, BiasDetector

# Initialize evaluator
evaluator = ThemisEvaluator()

# Add evaluators
evaluator.add_evaluator(HallucinationDetector())
evaluator.add_evaluator(BiasDetector())

# Run evaluation
results = evaluator.evaluate(
    model_outputs=["The sky is green.", "Paris is in France."],
    ground_truth=["The sky is blue.", "Paris is in France."],
    contexts=["Question about sky color", "Question about geography"]
)

print(results.summary())
```

### Model Comparison

```python
from themis.testing import ModelComparison
from themis.integrations import HuggingFaceIntegration

# Compare two models
comparison = ModelComparison()
hf_integration = HuggingFaceIntegration()

model_a = hf_integration.load_model("gpt2")
model_b = hf_integration.load_model("distilgpt2")

results = comparison.compare_models(
    models=[model_a, model_b],
    test_cases=["Tell me about AI", "What is Python?"],
    evaluators=["hallucination", "bias", "toxicity"]
)

# Statistical significance testing
significance = comparison.statistical_test(results)
print(f"Significant difference: {significance.is_significant}")
```

### Differential Privacy

```python
from themis.core.differential_privacy import LaplaceMechanism
from themis.core.differential_privacy.metrics import PrivacyAnalyzer

# Apply differential privacy
mechanism = LaplaceMechanism(epsilon=1.0)
private_output = mechanism.apply(sensitive_data="User's personal info")

# Analyze privacy guarantees
analyzer = PrivacyAnalyzer()
privacy_loss = analyzer.compute_privacy_loss(
    mechanism=mechanism,
    queries=["query1", "query2"]
)
```

### CLI Usage

```bash
# Run evaluation from command line
themis evaluate --model gpt-3.5-turbo --dataset data.json --output results.json

# Compare models
themis compare --models model1,model2 --evaluators hallucination,bias

# Generate report
themis report --results results.json --format html
```

## Evaluators

### Core Evaluators

| Evaluator | Description | Metrics |
|-----------|-------------|---------|
| `HallucinationDetector` | Detects factual inconsistencies | Accuracy, Consistency Score |
| `SemanticSimilarity` | Measures semantic similarity | Cosine Similarity, BERT Score |
| `PerformanceMetrics` | System performance evaluation | Latency, Memory Usage |
| `RobustnessTest` | Adversarial robustness testing | Attack Success Rate |

### Advanced Evaluators

| Evaluator | Description | Metrics |
|-----------|-------------|---------|
| `BiasDetector` | Identifies various bias types | Demographic Parity, Equalized Odds |
| `ToxicityDetector` | Content safety evaluation | Toxicity Score, Safety Rating |
| `FactualAccuracy` | Cross-references knowledge bases | Precision, Recall, F1 |
| `CoherenceAnalyzer` | Logical consistency analysis | Coherence Score, Flow Rating |

## Architecture

Themis follows a modular architecture with these key components:

- **Core Engine**: Orchestrates evaluation workflows
- **Evaluator Framework**: Pluggable evaluation modules
- **Integration Layer**: Connects with popular ML frameworks
- **Analytics Engine**: Processes and aggregates results
- **Privacy Module**: Differential privacy mechanisms
- **Testing Framework**: A/B testing and model comparison

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Development setup
git clone https://github.com/themis-ai/themis.git
cd themis
pip install -e .[dev]
pre-commit install

# Run tests
pytest tests/

# Format code
black themis/
isort themis/
```

## Documentation

- [Full Documentation](https://themis-ai.readthedocs.io/)
- [API Reference](https://themis-ai.readthedocs.io/en/latest/api.html)
- [Examples](examples/)
- [Tutorials](https://themis-ai.readthedocs.io/en/latest/tutorials.html)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use Themis in your research, please cite:

```bibtex
@software{themis2024,
  title={Themis: AI Evaluation and Testing Framework},
  author={Themis Team},
  year={2024},
  url={https://github.com/themis-ai/themis}
}
```

## Support

- [GitHub Issues](https://github.com/themis-ai/themis/issues)
- [Documentation](https://themis-ai.readthedocs.io/)
- [Discord Community](https://discord.gg/themis-ai)

---

Named after Themis, the Greek goddess of justice and divine order, this library aims to bring fairness, transparency, and rigorous evaluation to AI systems.