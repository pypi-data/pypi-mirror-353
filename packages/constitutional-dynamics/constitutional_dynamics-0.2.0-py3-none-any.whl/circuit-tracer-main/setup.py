#!/usr/bin/env python3
"""
Setup script for Circuit Tracer package
"""

from setuptools import setup, find_packages

setup(
    name="circuit_tracer",
    version="0.1.0",
    description="Library for circuit tracing in language models",
    packages=find_packages(include=['circuit_tracer', 'circuit_tracer.*']),
    package_dir={'': '.'},
    install_requires=[
        "einops>=0.8.0",
        "huggingface_hub>=0.26.0",
        "numpy>=2.0.0",
        "pydantic>=2.0.0",
        "pytest>=8.0.0",
        "safetensors>=0.5.0",
        "tokenizers>=0.21.0",
        "torch>=2.0.0",
        "tqdm>=4.60.0",
        "transformer-lens>=v2.15.4",
        "transformers>=4.50.0",
    ],
    entry_points={
        "console_scripts": [
            "circuit-tracer=circuit_tracer.__main__:main",
        ],
    },
)
