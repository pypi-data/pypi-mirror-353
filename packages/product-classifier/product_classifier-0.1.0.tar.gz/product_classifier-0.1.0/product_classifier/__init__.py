"""
CNN-BiLSTM Classifier Package

A hybrid CNN+BiLSTM architecture for product classification with attention mechanism.
"""

__version__ = "0.1.0"
__author__ = "Turgut Guvercin"
__email__ = "turgut430@gmail.com"

# Import main classes for easy access
from .inference import CNNBiLSTMInference
from .trainer import CNNBiLSTMTrainer
from .models.classifier import CNNBiLSTMClassifier
from .utils.tokenizer import WordTokenizer
from .utils.features import AdHocFeatureExtractor

# Define what gets imported with "from product_classifier import *"
__all__ = [
    "CNNBiLSTMInference",
    "CNNBiLSTMTrainer", 
    "CNNBiLSTMClassifier",
    "WordTokenizer",
    "AdHocFeatureExtractor",
]

# Package metadata
__title__ = "product_classifier"
__description__ = "CNN+BiLSTM hybrid architecture for product classification"
__url__ = "https://github.com/turgutguvercin/cnn-bilstm-classifier"
__license__ = "MIT"
__copyright__ = "Copyright 2025 Turgut Guvercin"

# Version info tuple
VERSION = tuple(map(int, __version__.split('.')))