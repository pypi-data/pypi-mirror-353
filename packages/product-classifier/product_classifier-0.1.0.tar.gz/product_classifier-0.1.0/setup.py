"""
setup.py for CNN-BiLSTM Classifier Package
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_long_description():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "CNN+BiLSTM hybrid architecture for product classification"

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "torch>=1.9.0",
            "numpy>=1.21.0",
            "safetensors>=0.3.0",
            "huggingface-hub>=0.15.0",
            "gensim>=4.0.0",
            "scikit-learn>=1.0.0",
            "tqdm>=4.60.0",
        ]

setup(
    name="product-classifier",
    version="0.1.0",
    author="Turgut Guvercin",
    author_email="turgut430@gmail.com",
    description="CNN+BiLSTM hybrid architecture for product classification",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/turgutguvercin/cnn-bilstm-classifier",
    project_urls={
        "Source Code": "https://github.com/turgutguvercin/cnn-bilstm-classifier",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "isort>=5.0",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "product-classifier-train=product_classifier.cli:train_cli",
            "product-classifier-predict=product_classifier.cli:predict_cli",
        ],
    },
    keywords=[
        "deep learning",
        "nlp",
        "text classification", 
        "cnn",
        "lstm",
        "product classification",
        "pytorch",
        "machine learning",
    ],
    include_package_data=True,
    zip_safe=False,
)