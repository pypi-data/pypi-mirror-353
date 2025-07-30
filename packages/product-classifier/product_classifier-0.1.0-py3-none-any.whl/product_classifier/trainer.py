"""
Training module for CNN+BiLSTM Classifier
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from tqdm import tqdm
import json
import os
import warnings
from typing import List, Dict, Tuple, Optional, Union
from sklearn.model_selection import train_test_split
from safetensors.torch import save_file
from huggingface_hub import HfApi, create_repo

from .models.classifier import CNNBiLSTMClassifier
from .utils.tokenizer import WordTokenizer
from .utils.features import AdHocFeatureExtractor

warnings.filterwarnings('ignore')


class ProductDataset(Dataset):
    """Dataset for product classification"""
    
    def __init__(
        self, 
        texts: List[str], 
        labels: List[int],
        tokenizer: WordTokenizer, 
        feature_extractor: AdHocFeatureExtractor,
        max_length: int = 50
    ):
        """
        Initialize dataset
        
        Args:
            texts: List of text strings
            labels: List of label integers
            tokenizer: Word tokenizer instance
            feature_extractor: Feature extractor instance
            max_length: Maximum sequence length
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.feature_extractor = feature_extractor
        self.max_length = max_length
        
        # Pre-encode all texts for efficiency
        print("Encoding texts...")
        self.encoded_texts = []
        for text in tqdm(texts, desc="Encoding"):
            encoded = self.tokenizer.encode(text, max_length)
            self.encoded_texts.append(encoded)
        
        # Pre-extract features
        print("Extracting features...")
        self.features = self.feature_extractor.extract_features(texts)
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        return {
            'text': torch.tensor(self.encoded_texts[idx], dtype=torch.long),
            'label': torch.tensor(self.labels[idx], dtype=torch.long),
            'features': torch.tensor(self.features[idx], dtype=torch.float32),
            'raw_text': self.texts[idx]
        }


class CNNBiLSTMTrainer:
    """
    Trainer class for CNN+BiLSTM classifier
    
    This class handles the complete training pipeline including data preparation,
    model initialization, training loop, validation, and model saving.
    
    Example:
        >>> trainer = CNNBiLSTMTrainer()
        >>> results = trainer.train(
        ...     df=your_dataframe,
        ...     text_column='product_name',
        ...     label_column='category'
        ... )
        >>> trainer.save_model('./my_model')
    """
    
    def __init__(self, device: Optional[str] = None):
        """
        Initialize trainer
        
        Args:
            device: Device to use for training ('cuda', 'cpu', or None for auto)
        """
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Will be set during training
        self.model = None
        self.tokenizer = None
        self.feature_extractor = None
        self.category_to_label = None
        self.label_to_category = None
        self.config = None
        self.training_history = None
        
    def prepare_data(
        self,
        df: pd.DataFrame,
        text_column: str,
        label_column: str,
        test_size: float = 0.25,
        min_samples_per_class: int = 2
    ) -> Tuple[List[str], List[str], List[int], List[int], Dict, Dict]:
        """
        Prepare data for training
        
        Args:
            df: Input dataframe
            text_column: Name of text column
            label_column: Name of label column
            test_size: Fraction for validation set
            min_samples_per_class: Minimum samples per class
            
        Returns:
            Tuple of train_texts, val_texts, train_labels, val_labels, category_to_label, config
        """
        print("Preparing data...")
        
        # Clean data
        df_clean = df.dropna(subset=[text_column, label_column]).copy()
        print(f"Dataset size after removing NaN: {len(df_clean)}")
        
        # Filter classes with minimum samples
        label_counts = df_clean[label_column].value_counts()
        valid_labels = label_counts[label_counts >= min_samples_per_class].index
        df_clean = df_clean[df_clean[label_column].isin(valid_labels)]
        print(f"Dataset size after filtering classes: {len(df_clean)}")
        print(f"Number of classes: {len(valid_labels)}")
        
        # Extract texts
        texts = df_clean[text_column].astype(str).tolist()
        
        # Create label mappings
        unique_categories = sorted(df_clean[label_column].unique())
        category_to_label = {cat: idx for idx, cat in enumerate(unique_categories)}
        label_to_category = {idx: cat for cat, idx in category_to_label.items()}
        labels = [category_to_label[cat] for cat in df_clean[label_column]]
        
        print(f"Label distribution:")
        for cat, count in label_counts[valid_labels].head(10).items():
            print(f"  {cat}: {count}")
        if len(valid_labels) > 10:
            print(f"  ... and {len(valid_labels) - 10} more classes")
        
        # Split data
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=test_size, stratify=labels, random_state=42
        )
        
        print(f"Train samples: {len(train_texts)}")
        print(f"Validation samples: {len(val_texts)}")
        
        return (
            train_texts, val_texts, train_labels, val_labels,
            category_to_label, label_to_category
        )
    
    def create_tokenizer(self, texts: List[str], embedding_dim: int = 512) -> WordTokenizer:
        """Create and train Word2Vec tokenizer"""
        print("Creating tokenizer...")
        return WordTokenizer(texts, embedding_dim=embedding_dim)
    
    def train_epoch(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        criterion: nn.Module,
        optimizer: torch.optim.Optimizer,
        epoch: int
    ) -> Tuple[float, float]:
        """Train for one epoch"""
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        progress_bar = tqdm(
            train_loader,
            desc=f"Epoch {epoch}",
            leave=False
        )
        
        for batch in progress_bar:
            texts = batch['text'].to(self.device)
            labels = batch['label'].to(self.device)
            features = batch['features'].to(self.device)
            
            optimizer.zero_grad()
            outputs = model(texts, features)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            # Update progress bar
            progress_bar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100.*correct/total:.2f}%'
            })
        
        avg_loss = total_loss / len(train_loader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def validate(
        self,
        model: nn.Module,
        val_loader: DataLoader,
        criterion: nn.Module
    ) -> Tuple[float, float]:
        """Validate the model"""
        model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validating", leave=False):
                texts = batch['text'].to(self.device)
                labels = batch['label'].to(self.device)
                features = batch['features'].to(self.device)
                
                outputs = model(texts, features)
                loss = criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def train(
        self,
        df: pd.DataFrame,
        text_column: str = 'text',
        label_column: str = 'label',
        test_size: float = 0.25,
        config: Optional[Dict] = None
    ) -> Dict:
        """
        Train the CNN+BiLSTM model
        
        Args:
            df: Input dataframe with text and labels
            text_column: Name of column containing text
            label_column: Name of column containing labels
            test_size: Fraction for validation set
            config: Training configuration dictionary
            
        Returns:
            Dict: Training results including model, tokenizer, etc.
        """
        
        # Default configuration
        if config is None:
            config = {
                'batch_size': 128,
                'epochs': 20,
                'learning_rate': 0.001,
                'embedding_dim': 512,
                'cnn_filters': 128,
                'lstm_hidden': 256,
                'max_length': 50,
                'min_count': 2,
                'patience': 5
            }
        
        self.config = config
        print(f"Training configuration: {config}")
        
        # Prepare data
        (train_texts, val_texts, train_labels, val_labels,
         category_to_label, label_to_category) = self.prepare_data(
            df, text_column, label_column, test_size
        )
        
        self.category_to_label = category_to_label
        self.label_to_category = label_to_category
        num_classes = len(category_to_label)
        
        # Create tokenizer
        all_texts = train_texts + val_texts
        self.tokenizer = self.create_tokenizer(all_texts, config['embedding_dim'])
        
        # Create feature extractor
        self.feature_extractor = AdHocFeatureExtractor()
        
        # Create datasets
        train_dataset = ProductDataset(
            train_texts, train_labels, self.tokenizer,
            self.feature_extractor, config['max_length']
        )
        val_dataset = ProductDataset(
            val_texts, val_labels, self.tokenizer,
            self.feature_extractor, config['max_length']
        )
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset, 
            batch_size=config['batch_size'], 
            shuffle=True,
            num_workers=0  # Set to 0 for compatibility
        )
        val_loader = DataLoader(
            val_dataset, 
            batch_size=config['batch_size'], 
            shuffle=False,
            num_workers=0
        )
        
        # Initialize model
        print("Initializing model...")
        self.model = CNNBiLSTMClassifier(
            vocab_size=self.tokenizer.vocab_size,
            num_classes=num_classes,
            embedding_matrix=self.tokenizer.embedding_matrix,
            embedding_dim=config['embedding_dim'],
            cnn_filters=config['cnn_filters'],
            lstm_hidden=config['lstm_hidden'],
            adhoc_features_dim=self.feature_extractor.get_num_features()
        )
        self.model = self.model.to(self.device)
        
        # Training setup
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=config['learning_rate'])
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, patience=config.get('patience', 3), factor=0.5, verbose=True
        )
        
        # Training loop
        print(f"\nStarting training for {config['epochs']} epochs...")
        best_val_acc = 0
        best_model_state = None
        history = {
            'train_loss': [], 'train_acc': [],
            'val_loss': [], 'val_acc': []
        }
        
        for epoch in range(1, config['epochs'] + 1):
            print(f"\nEpoch {epoch}/{config['epochs']}")
            
            # Train
            train_loss, train_acc = self.train_epoch(
                self.model, train_loader, criterion, optimizer, epoch
            )
            
            # Validate
            val_loss, val_acc = self.validate(self.model, val_loader, criterion)
            
            # Update scheduler
            scheduler.step(val_loss)
            
            # Save history
            history['train_loss'].append(train_loss)
            history['train_acc'].append(train_acc)
            history['val_loss'].append(val_loss)
            history['val_acc'].append(val_acc)
            
            # Print results
            print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
            print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_model_state = self.model.state_dict().copy()
                print(f"🎉 New best validation accuracy: {val_acc:.4f}")
        
        # Load best model
        if best_model_state is not None:
            self.model.load_state_dict(best_model_state)
        
        self.training_history = history
        
        print(f"\n✅ Training completed!")
        print(f"Best validation accuracy: {best_val_acc:.4f}")
        
        return {
            'model': self.model,
            'tokenizer': self.tokenizer,
            'feature_extractor': self.feature_extractor,
            'category_to_label': self.category_to_label,
            'label_to_category': self.label_to_category,
            'config': self.config,
            'best_val_acc': best_val_acc,
            'history': history
        }
    
    def save_model(self, save_directory: str) -> str:
        """
        Save trained model to directory
        
        Args:
            save_directory: Directory to save model files
            
        Returns:
            str: Path to saved directory
        """
        if self.model is None:
            raise ValueError("No trained model found. Train a model first.")
        
        os.makedirs(save_directory, exist_ok=True)
        print(f"Saving model to {save_directory}...")
        
        # 1. Save model weights as SafeTensors
        model_path = os.path.join(save_directory, "model.safetensors")
        save_file(self.model.state_dict(), model_path)
        
        # 2. Save tokenizer
        tokenizer_data = {
            'word2idx': self.tokenizer.word2idx,
            'idx2word': self.tokenizer.idx2word,
            'vocab_size': self.tokenizer.vocab_size,
            'embedding_dim': self.tokenizer.embedding_dim,
            'embedding_matrix': self.tokenizer.embedding_matrix.tolist()
        }
        
        with open(os.path.join(save_directory, "tokenizer.json"), 'w', encoding='utf-8') as f:
            json.dump(tokenizer_data, f, ensure_ascii=False, indent=2)
        
        # 3. Save label mappings
        label_mappings = {
            'category_to_label': {str(k): int(v) for k, v in self.category_to_label.items()},
            'label_to_category': {int(v): str(k) for k, v in self.category_to_label.items()},
            'num_classes': len(self.category_to_label)
        }
        
        with open(os.path.join(save_directory, "label_mappings.json"), 'w', encoding='utf-8') as f:
            json.dump(label_mappings, f, ensure_ascii=False, indent=2)
        
        # 4. Save config
        model_config = {
            'vocab_size': self.tokenizer.vocab_size,
            'num_classes': len(self.category_to_label),
            'embedding_dim': self.config['embedding_dim'],
            'cnn_filters': self.config['cnn_filters'],
            'lstm_hidden': self.config['lstm_hidden'],
            'max_length': self.config['max_length'],
            'adhoc_features_dim': self.feature_extractor.get_num_features(),
            'kernel_sizes': [2, 3, 4, 5],
            'training_config': self.config
        }
        
        if self.training_history:
            model_config['best_val_acc'] = max(self.training_history['val_acc'])
        
        with open(os.path.join(save_directory, "config.json"), 'w') as f:
            json.dump(model_config, f, indent=2)
        
        # 5. Save training history
        if self.training_history:
            with open(os.path.join(save_directory, "training_history.json"), 'w') as f:
                json.dump(self.training_history, f, indent=2)
        
        # 6. Create README
        self._create_model_readme(save_directory)
        
        print(f"✅ Model saved successfully to {save_directory}")
        return save_directory
    
    def save_to_hub(
        self,
        repo_name: str,
        private: bool = False,
        commit_message: str = "Upload CNN+BiLSTM classifier"
    ) -> str:
        """
        Save model to HuggingFace Hub
        
        Args:
            repo_name: Repository name (username/model-name)
            private: Whether to make repository private
            commit_message: Commit message
            
        Returns:
            str: URL to the repository
        """
        if self.model is None:
            raise ValueError("No trained model found. Train a model first.")
        
        # Save to temporary directory first
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            self.save_model(temp_dir)
            
            # Upload to hub
            try:
                api = HfApi()
                
                print(f"Creating repository: {repo_name}")
                create_repo(
                    repo_id=repo_name,
                    repo_type="model",
                    private=private,
                    exist_ok=True
                )
                
                print("Uploading files to HuggingFace Hub...")
                api.upload_folder(
                    folder_path=temp_dir,
                    repo_id=repo_name,
                    repo_type="model",
                    commit_message=commit_message
                )
                
                url = f"https://huggingface.co/{repo_name}"
                print(f"✅ Model uploaded successfully to {url}")
                return url
                
            except Exception as e:
                print(f"❌ Error uploading to HuggingFace Hub: {e}")
                raise
    
    def _create_model_readme(self, save_directory: str):
        """Create README file for the model"""
        if not self.config or not self.tokenizer:
            return
        
        best_acc = 0.0
        if self.training_history:
            best_acc = max(self.training_history['val_acc'])
        
        readme_content = f"""---
license: mit
library_name: pytorch
tags:
- product-classification
- cnn-bilstm
- text-classification
pipeline_tag: text-classification
---

# CNN + BiLSTM Product Classification Model

This model uses a hybrid CNN + BiLSTM architecture for product classification.

## Model Details
- **Architecture**: Multi-kernel CNN + Bidirectional LSTM with attention
- **Embedding Dimension**: {self.config['embedding_dim']}
- **Vocabulary Size**: {self.tokenizer.vocab_size:,}
- **Number of Classes**: {len(self.category_to_label):,}
- **Best Validation Accuracy**: {best_acc:.4f}

## Usage

```python
from product_classifier import CNNBiLSTMInference

# Load the model
model = CNNBiLSTMInference.from_local("./path/to/model")

# Make predictions
predictions = model.predict([
    "Sample product title 1",
    "Sample product title 2"
], top_k=3)

for text, pred in zip(texts, predictions):
    print(f"Text: {{text}}")
    for label, score in pred:
        print(f"  → {{label}}: {{score:.4f}}")
```

## Training Configuration
- **Epochs**: {self.config.get('epochs', 'N/A')}
- **Batch Size**: {self.config.get('batch_size', 'N/A')}
- **Learning Rate**: {self.config.get('learning_rate', 'N/A')}
- **CNN Filters**: {self.config.get('cnn_filters', 'N/A')}
- **LSTM Hidden**: {self.config.get('lstm_hidden', 'N/A')}
"""
        
        with open(os.path.join(save_directory, "README.md"), 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def load_model(self, model_path: str):
        """Load a previously saved model"""
        from .inference import CNNBiLSTMInference
        
        # Load the inference wrapper
        inference = CNNBiLSTMInference.from_local(model_path)
        
        # Set trainer attributes
        self.model = inference.model
        self.tokenizer = inference.tokenizer
        self.feature_extractor = inference.feature_extractor
        self.config = inference.config
        
        # Recreate label mappings
        self.category_to_label = {
            str(k): int(v) for k, v in inference.label_mappings['category_to_label'].items()
        }
        self.label_to_category = {
            int(k): str(v) for k, v in inference.label_mappings['label_to_category'].items()
        }
        
        print(f"✅ Model loaded from {model_path}")
        return inference
    
    def get_training_summary(self) -> Dict:
        """Get summary of training results"""
        if not self.training_history:
            return {"error": "No training history available"}
        
        history = self.training_history
        return {
            "epochs_trained": len(history['train_loss']),
            "best_train_acc": max(history['train_acc']),
            "best_val_acc": max(history['val_acc']),
            "final_train_loss": history['train_loss'][-1],
            "final_val_loss": history['val_loss'][-1],
            "num_classes": len(self.category_to_label) if self.category_to_label else 0,
            "vocab_size": self.tokenizer.vocab_size if self.tokenizer else 0
        }
    
    def plot_training_history(self, save_path: Optional[str] = None):
        """Plot training history"""
        if not self.training_history:
            print("No training history available")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            history = self.training_history
            epochs = range(1, len(history['train_loss']) + 1)
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            
            # Plot loss
            ax1.plot(epochs, history['train_loss'], 'b-', label='Training Loss')
            ax1.plot(epochs, history['val_loss'], 'r-', label='Validation Loss')
            ax1.set_title('Model Loss')
            ax1.set_xlabel('Epoch')
            ax1.set_ylabel('Loss')
            ax1.legend()
            ax1.grid(True)
            
            # Plot accuracy
            ax2.plot(epochs, history['train_acc'], 'b-', label='Training Accuracy')
            ax2.plot(epochs, history['val_acc'], 'r-', label='Validation Accuracy')
            ax2.set_title('Model Accuracy')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('Accuracy')
            ax2.legend()
            ax2.grid(True)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Training plot saved to {save_path}")
            else:
                plt.show()
                
        except ImportError:
            print("matplotlib not available. Install with: pip install matplotlib")