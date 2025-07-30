#!/usr/bin/env python3
"""
Themis - AI Evaluation and Testing Framework
"""

from setuptools import setup, find_packages
import os
import sys

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Version
version = '1.0'

# Requirements
install_requires = [
    'numpy>=1.21.0',
    'pandas>=1.3.0',
    'scikit-learn>=1.0.0',
    'torch>=1.9.0',
    'transformers>=4.12.0',
    'datasets>=1.16.0',
    'nltk>=3.6',
    'spacy>=3.4.0',
    'sentence-transformers>=2.2.0',
    'openai>=0.27.0',
    'fastapi>=0.75.0',
    'uvicorn>=0.17.0',
    'mlflow>=1.20.0',
    'requests>=2.25.0',
    'tqdm>=4.62.0',
    'plotly>=5.0.0',
    'matplotlib>=3.4.0',
    'seaborn>=0.11.0',
    'pyyaml>=6.0',
    'click>=8.0.0',
    'jinja2>=3.0.0',
    'jsonschema>=4.0.0',
    'scipy>=1.7.0',
    'networkx>=2.6.0',
    'python-dotenv>=0.19.0',
]

extras_require = {
    'dev': [
        'pytest>=6.2.0',
        'pytest-cov>=3.0.0',
        'black>=22.0.0',
        'flake8>=4.0.0',
        'isort>=5.10.0',
        'mypy>=0.910',
        'pre-commit>=2.15.0',
    ],
    'docs': [
        'sphinx>=4.0.0',
        'sphinx-rtd-theme>=1.0.0',
        'sphinx-autodoc-typehints>=1.12.0',
    ],
    'full': [
        'tensorboard>=2.7.0',
        'wandb>=0.12.0',
        'ray>=1.9.0',
    ]
}

# Add all extras to 'all'
extras_require['all'] = sum(extras_require.values(), [])

setup(
    name='themis-ai-eval',
    version=version,
    description='Comprehensive AI System Evaluation & Testing Framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Themis Team',
    author_email='contact@themis-ai.dev',
    url='https://github.com/themis-ai/themis',
    project_urls={
        'Documentation': 'https://themis-ai.readthedocs.io/',
        'Source': 'https://github.com/themis-ai/themis',
        'Tracker': 'https://github.com/themis-ai/themis/issues',
    },
    packages=find_packages(exclude=['tests*', 'examples*']),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.8',
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'themis=themis.cli.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
    ],
    keywords='ai, ml, evaluation, testing, llm, bias, differential-privacy',
    license='MIT',
)