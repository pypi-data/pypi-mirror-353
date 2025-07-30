"""
Inference module for CNN+BiLSTM Classifier
"""

import torch
import torch.nn.functional as F
import numpy as np
import json
import os
from safetensors.torch import load_file
from huggingface_hub import hf_hub_download
from typing import List, Dict, Tuple, Union, Optional

from .models.classifier import CNNBiLSTMClassifier
from .utils.tokenizer import WordTokenizer
from .utils.features import AdHocFeatureExtractor


class CNNBiLSTMInference:
    """
    Inference wrapper for the CNN+BiLSTM model
    
    This class provides an easy-to-use interface for loading and running
    inference with the CNN+BiLSTM product classification model.
    
    Example:
        >>> from product_classifier import CNNBiLSTMInference
        >>> 
        >>> # Load from HuggingFace Hub
        >>> model = CNNBiLSTMInference.from_pretrained("turgutguvercin/product-classifier-v1")
        >>> 
        >>> # Make predictions
        >>> predictions = model.predict("Yataş Bedding BAMBU Yorgan", top_k=3)
        >>> print(predictions)
    """
    
    def __init__(
        self,
        model: CNNBiLSTMClassifier,
        tokenizer: WordTokenizer,
        feature_extractor: AdHocFeatureExtractor,
        label_mappings: Dict,
        config: Dict,
        device: Optional[str] = None
    ):
        """
        Initialize inference wrapper
        
        Args:
            model: The CNN+BiLSTM model
            tokenizer: Word tokenizer
            feature_extractor: Feature extractor for ad-hoc features
            label_mappings: Label to category mappings
            config: Model configuration
            device: Device to run inference on
        """
        self.model = model
        self.tokenizer = tokenizer
        self.feature_extractor = feature_extractor
        self.label_mappings = label_mappings
        self.config = config
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.model.to(self.device)
        self.model.eval()
        
        # Create label mapping
        self.label_to_category = {
            int(k): str(v) for k, v in label_mappings['label_to_category'].items()
        }
    
    @classmethod
    def from_pretrained(
        cls,
        repo_id: str,
        device: Optional[str] = None,
        cache_dir: Optional[str] = None,
        force_download: bool = False
    ):
        """
        Load model from HuggingFace Hub
        
        Args:
            repo_id: HuggingFace model repository ID (e.g., "turgutguvercin/product-classifier-v1")
            device: Device to load model on ("cuda", "cpu", or None for auto)
            cache_dir: Directory to cache downloaded files
            force_download: Force re-download even if cached
            
        Returns:
            CNNBiLSTMInference: Loaded inference wrapper
            
        Example:
            >>> model = CNNBiLSTMInference.from_pretrained(
            ...     "username/cnn-bilstm-classifier",
            ...     device="cuda"
            ... )
        """
        
        # Download files from HuggingFace Hub
        model_file = hf_hub_download(
            repo_id, "model.safetensors",
            cache_dir=cache_dir,
            force_download=force_download
        )
        tokenizer_file = hf_hub_download(
            repo_id, "tokenizer.json",
            cache_dir=cache_dir,
            force_download=force_download
        )
        mappings_file = hf_hub_download(
            repo_id, "label_mappings.json",
            cache_dir=cache_dir,
            force_download=force_download
        )
        config_file = hf_hub_download(
            repo_id, "config.json",
            cache_dir=cache_dir,
            force_download=force_download
        )
        
        # Load configuration
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Load tokenizer
        with open(tokenizer_file, 'r', encoding='utf-8') as f:
            tokenizer_data = json.load(f)
        
        tokenizer = WordTokenizer(
            word2idx=tokenizer_data['word2idx'],
            idx2word={int(k): v for k, v in tokenizer_data['idx2word'].items()},
            vocab_size=tokenizer_data['vocab_size'],
            embedding_dim=tokenizer_data['embedding_dim']
        )
        
        # Load label mappings
        with open(mappings_file, 'r', encoding='utf-8') as f:
            label_mappings = json.load(f)
        
        # Create model
        embedding_matrix = np.array(tokenizer_data['embedding_matrix'])
        model = CNNBiLSTMClassifier(
            vocab_size=config['vocab_size'],
            num_classes=config['num_classes'],
            embedding_matrix=embedding_matrix,
            embedding_dim=config['embedding_dim'],
            cnn_filters=config['cnn_filters'],
            lstm_hidden=config['lstm_hidden'],
            adhoc_features_dim=config['adhoc_features_dim']
        )
        
        # Load model weights
        state_dict = load_file(model_file)
        model.load_state_dict(state_dict)
        
        # Create feature extractor
        feature_extractor = AdHocFeatureExtractor()
        
        return cls(model, tokenizer, feature_extractor, label_mappings, config, device)
    
    @classmethod
    def from_local(cls, model_dir: str, device: Optional[str] = None):
        """
        Load model from local directory
        
        Args:
            model_dir: Path to directory containing model files
            device: Device to load model on
            
        Returns:
            CNNBiLSTMInference: Loaded inference wrapper
        """
        # Load files from local directory
        config_file = os.path.join(model_dir, "config.json")
        tokenizer_file = os.path.join(model_dir, "tokenizer.json")
        mappings_file = os.path.join(model_dir, "label_mappings.json")
        model_file = os.path.join(model_dir, "model.safetensors")
        
        # Verify all files exist
        for file_path in [config_file, tokenizer_file, mappings_file, model_file]:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Required file not found: {file_path}")
        
        # Load configuration
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Load tokenizer
        with open(tokenizer_file, 'r', encoding='utf-8') as f:
            tokenizer_data = json.load(f)
        
        tokenizer = WordTokenizer(
            word2idx=tokenizer_data['word2idx'],
            idx2word={int(k): v for k, v in tokenizer_data['idx2word'].items()},
            vocab_size=tokenizer_data['vocab_size'],
            embedding_dim=tokenizer_data['embedding_dim']
        )
        
        # Load label mappings
        with open(mappings_file, 'r', encoding='utf-8') as f:
            label_mappings = json.load(f)
        
        # Create model
        embedding_matrix = np.array(tokenizer_data['embedding_matrix'])
        model = CNNBiLSTMClassifier(
            vocab_size=config['vocab_size'],
            num_classes=config['num_classes'],
            embedding_matrix=embedding_matrix,
            embedding_dim=config['embedding_dim'],
            cnn_filters=config['cnn_filters'],
            lstm_hidden=config['lstm_hidden'],
            adhoc_features_dim=config['adhoc_features_dim']
        )
        
        # Load model weights
        state_dict = load_file(model_file)
        model.load_state_dict(state_dict)
        
        # Create feature extractor
        feature_extractor = AdHocFeatureExtractor()
        
        return cls(model, tokenizer, feature_extractor, label_mappings, config, device)
    
    def predict(
        self,
        texts: Union[str, List[str]],
        top_k: int = 1,
        return_probabilities: bool = True
    ) -> Union[Tuple, List[Tuple]]:
        """
        Predict categories for input texts
        
        Args:
            texts: Single text or list of texts to classify
            top_k: Number of top predictions to return per text
            return_probabilities: Whether to return confidence scores
            
        Returns:
            For single text: tuple or list of tuples (label, score)
            For multiple texts: list of predictions
            
        Example:
            >>> # Single prediction
            >>> prediction = model.predict("Yataş Bedding BAMBU Yorgan", top_k=3)
            >>> print(prediction)  # [("category1", 0.85), ("category2", 0.10), ...]
            >>> 
            >>> # Batch prediction
            >>> predictions = model.predict(["text1", "text2"], top_k=1)
            >>> print(predictions)  # [("category1", 0.85), ("category3", 0.92)]
        """
        single_input = isinstance(texts, str)
        if single_input:
            texts = [texts]
        
        # Encode texts
        encoded = [
            self.tokenizer.encode(text, max_length=self.config['max_length']) 
            for text in texts
        ]
        encoded_tensor = torch.tensor(encoded, dtype=torch.long).to(self.device)
        
        # Extract ad-hoc features
        adhoc_features = self.feature_extractor.extract_features(texts)
        adhoc_tensor = torch.tensor(adhoc_features, dtype=torch.float32).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(encoded_tensor, adhoc_tensor)
            probs = F.softmax(outputs, dim=1)
            
            top_probs, top_indices = torch.topk(probs, k=top_k, dim=1)
        
        # Format results
        predictions = []
        for i in range(len(texts)):
            pred = []
            for j in range(top_k):
                label_idx = top_indices[i][j].item()
                prob = top_probs[i][j].item()
                label = self.label_to_category[label_idx]
                
                if return_probabilities:
                    pred.append((label, prob))
                else:
                    pred.append(label)
            
            predictions.append(pred if top_k > 1 else pred[0])
        
        return predictions[0] if single_input else predictions
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model
        
        Returns:
            Dict: Model information including architecture details
        """
        return {
            "model_type": "CNN+BiLSTM Classifier",
            "vocab_size": self.tokenizer.vocab_size,
            "embedding_dim": self.config['embedding_dim'],
            "num_classes": self.config['num_classes'],
            "cnn_filters": self.config['cnn_filters'],
            "lstm_hidden": self.config['lstm_hidden'],
            "max_length": self.config['max_length'],
            "device": self.device,
            "best_val_acc": self.config.get('best_val_acc', 'N/A')
        }
    
    def __repr__(self) -> str:
        """String representation of the inference wrapper"""
        info = self.get_model_info()
        return (
            f"CNNBiLSTMInference(\n"
            f"  vocab_size={info['vocab_size']},\n"
            f"  num_classes={info['num_classes']},\n"
            f"  embedding_dim={info['embedding_dim']},\n"
            f"  device='{info['device']}'\n"
            f")"
        )