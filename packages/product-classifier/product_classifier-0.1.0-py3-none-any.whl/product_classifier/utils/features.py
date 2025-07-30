"""
Feature extraction utilities for CNN+BiLSTM Classifier
"""

import numpy as np
from typing import List


class AdHocFeatureExtractor:
    """
    Extract ad-hoc features from text as described in the paper
    
    This class extracts various statistical and linguistic features from
    product titles including length statistics, character distributions,
    and word-level features.
    """
    
    def __init__(self):
        """Initialize the feature extractor"""
        self.feature_names = [
            "title_length",
            "uppercase_rate", 
            "alphabet_rate",
            "digit_rate",
            "space_count",
            "space_rate",
            "word_count",
            "max_word_length",
            "unique_word_rate",
            "symbol_count",
            "word_len_hist_0_4",
            "word_len_hist_4_8", 
            "word_len_hist_8_12",
            "word_len_hist_12_16",
            "word_len_hist_16_20"
        ]
    
    def extract_features(self, texts: List[str]) -> np.ndarray:
        """
        Extract ad-hoc features from a list of texts
        
        Args:
            texts: List of text strings to extract features from
            
        Returns:
            np.ndarray: Feature matrix of shape (len(texts), num_features)
        """
        features = []
        
        for text in texts:
            text_features = self._extract_single_text_features(text)
            features.append(text_features)
        
        return np.array(features, dtype=np.float32)
    
    def _extract_single_text_features(self, text: str) -> List[float]:
        """
        Extract features from a single text
        
        Args:
            text: Input text string
            
        Returns:
            List[float]: List of extracted features
        """
        text_features = []
        text = str(text)  # Ensure text is string
        
        # Basic text statistics
        text_length = len(text)
        text_features.append(text_length)
        
        # Character-level statistics
        if text_length > 0:
            # Uppercase rate
            uppercase_count = sum(1 for c in text if c.isupper())
            text_features.append(uppercase_count / text_length)
            
            # Alphabet rate
            alpha_count = sum(1 for c in text if c.isalpha())
            text_features.append(alpha_count / text_length)
            
            # Digit rate
            digit_count = sum(1 for c in text if c.isdigit())
            text_features.append(digit_count / text_length)
            
            # Space statistics
            space_count = text.count(' ')
            text_features.append(space_count)
            text_features.append(space_count / text_length)
        else:
            # Handle empty text
            text_features.extend([0.0, 0.0, 0.0, 0.0, 0.0])
        
        # Word-level statistics
        words = text.split()
        word_count = len(words)
        text_features.append(word_count)
        
        if words:
            # Max word length
            max_word_len = max(len(word) for word in words)
            text_features.append(max_word_len)
            
            # Unique word rate
            unique_words = len(set(words))
            text_features.append(unique_words / word_count)
        else:
            # Handle text with no words
            text_features.extend([0.0, 0.0])
        
        # Symbol count (non-alphanumeric, non-space characters)
        symbol_count = sum(1 for c in text if not c.isalnum() and not c.isspace())
        text_features.append(symbol_count)
        
        # Word length histogram (5 bins: 0-4, 4-8, 8-12, 12-16, 16-20)
        if words:
            word_lens = [len(word) for word in words]
            hist, _ = np.histogram(word_lens, bins=5, range=(0, 20))
            text_features.extend(hist.tolist())
        else:
            # Empty histogram for texts with no words
            text_features.extend([0, 0, 0, 0, 0])
        
        return text_features
    
    def get_feature_names(self) -> List[str]:
        """
        Get names of all extracted features
        
        Returns:
            List[str]: List of feature names
        """
        return self.feature_names.copy()
    
    def get_num_features(self) -> int:
        """
        Get the number of features extracted
        
        Returns:
            int: Number of features (should be 15)
        """
        return len(self.feature_names)
    
    def describe_features(self) -> str:
        """
        Get a description of all extracted features
        
        Returns:
            str: Human-readable description of features
        """
        descriptions = {
            "title_length": "Total number of characters in the text",
            "uppercase_rate": "Ratio of uppercase characters to total characters",
            "alphabet_rate": "Ratio of alphabetic characters to total characters", 
            "digit_rate": "Ratio of digit characters to total characters",
            "space_count": "Total number of space characters",
            "space_rate": "Ratio of space characters to total characters",
            "word_count": "Total number of words (space-separated tokens)",
            "max_word_length": "Length of the longest word",
            "unique_word_rate": "Ratio of unique words to total words",
            "symbol_count": "Number of non-alphanumeric, non-space characters",
            "word_len_hist_0_4": "Count of words with length 0-4 characters",
            "word_len_hist_4_8": "Count of words with length 4-8 characters",
            "word_len_hist_8_12": "Count of words with length 8-12 characters", 
            "word_len_hist_12_16": "Count of words with length 12-16 characters",
            "word_len_hist_16_20": "Count of words with length 16-20 characters"
        }
        
        result = "Ad-hoc Features:\n" + "=" * 50 + "\n"
        for i, (name, desc) in enumerate(descriptions.items()):
            result += f"{i+1:2d}. {name:20s}: {desc}\n"
        
        return result
    
    def __len__(self) -> int:
        """Return the number of features"""
        return self.get_num_features()
    
    def __repr__(self) -> str:
        """String representation of the feature extractor"""
        return f"AdHocFeatureExtractor(num_features={self.get_num_features()})"