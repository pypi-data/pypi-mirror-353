from typing import List
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class MultiKernelCNN(nn.Module):
    """Multi-kernel CNN as described in the paper"""
    
    def __init__(self, embedding_dim: int, num_filters: int = 128,
                 kernel_sizes: List[int] = [2, 3, 4, 5]):
        super().__init__()
        
        self.convs = nn.ModuleList([
            nn.Conv1d(embedding_dim, num_filters, kernel_size)
            for kernel_size in kernel_sizes
        ])
        
        self.dropout = nn.Dropout(0.5)
        self.output_dim = len(kernel_sizes) * num_filters
    
    def forward(self, x):
        # x shape: (batch_size, seq_len, embedding_dim)
        x = x.transpose(1, 2)  # (batch_size, embedding_dim, seq_len)
        
        conv_outputs = []
        for conv in self.convs:
            # Apply convolution and ReLU
            conv_out = F.relu(conv(x))  # (batch_size, num_filters, new_seq_len)
            # Max pooling over sequence
            pooled = F.max_pool1d(conv_out, conv_out.size(2)).squeeze(2)
            conv_outputs.append(pooled)
        
        # Concatenate all features
        output = torch.cat(conv_outputs, dim=1)
        output = self.dropout(output)
        
        return output

class BiLSTMWithAttention(nn.Module):
    """Bidirectional LSTM with soft attention"""
    
    def __init__(self, embedding_dim: int, hidden_dim: int = 256,
                 num_layers: int = 2, dropout: float = 0.5):
        super().__init__()
        
        self.lstm = nn.LSTM(
            embedding_dim, hidden_dim, num_layers,
            batch_first=True, bidirectional=True, dropout=dropout
        )
        
        # Attention layer
        self.attention = nn.Linear(hidden_dim * 2, 1)
        self.dropout = nn.Dropout(dropout)
        self.output_dim = hidden_dim * 2
    
    def forward(self, x, lengths=None):
        # x shape: (batch_size, seq_len, embedding_dim)
        lstm_out, _ = self.lstm(x)
        # lstm_out shape: (batch_size, seq_len, hidden_dim * 2)
        
        # Attention mechanism
        attention_scores = self.attention(lstm_out).squeeze(-1)
        # attention_scores shape: (batch_size, seq_len)
        
        # Mask padding if lengths provided
        if lengths is not None:
            mask = self.create_mask(lstm_out.size(0), lstm_out.size(1), lengths)
            attention_scores = attention_scores.masked_fill(~mask, float('-inf'))
        
        attention_weights = F.softmax(attention_scores, dim=1)
        # attention_weights shape: (batch_size, seq_len)
        
        # Weighted sum of LSTM outputs
        weighted_output = torch.bmm(
            attention_weights.unsqueeze(1), lstm_out
        ).squeeze(1)
        # weighted_output shape: (batch_size, hidden_dim * 2)
        
        output = self.dropout(weighted_output)
        return output
    
    def create_mask(self, batch_size, max_len, lengths):
        mask = torch.arange(max_len).expand(batch_size, max_len).to(lengths.device)
        mask = mask < lengths.unsqueeze(1)
        return mask

class CNNBiLSTMClassifier(nn.Module):
    """Combined CNN + BiLSTM model as per the paper"""
    
    def __init__(self, vocab_size: int, num_classes: int, embedding_matrix: np.ndarray,
                 embedding_dim: int = 512, cnn_filters: int = 128,
                 lstm_hidden: int = 256, adhoc_features_dim: int = 20,
                 freeze_embeddings: bool = False):
        super().__init__()
        
        # Embedding layer with pre-trained weights
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.embedding.weight.data.copy_(torch.from_numpy(embedding_matrix))
        if freeze_embeddings:
            self.embedding.weight.requires_grad = False
        
        # Multi-kernel CNN
        self.cnn = MultiKernelCNN(embedding_dim, cnn_filters)
        
        # BiLSTM with attention
        self.bilstm = BiLSTMWithAttention(embedding_dim, lstm_hidden)
        
        # MLP for ad-hoc features
        self.adhoc_mlp = nn.Sequential(
            nn.Linear(adhoc_features_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(64, 32)
        )
        
        # Final classifier
        concat_dim = self.cnn.output_dim + self.bilstm.output_dim + 32
        self.classifier = nn.Sequential(
            nn.Linear(concat_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x, adhoc_features, lengths=None):
        # x shape: (batch_size, seq_len)
        
        # Embedding
        embedded = self.embedding(x)
        # embedded shape: (batch_size, seq_len, embedding_dim)
        
        # CNN branch
        cnn_output = self.cnn(embedded)
        
        # BiLSTM branch
        bilstm_output = self.bilstm(embedded, lengths)
        
        # Ad-hoc features branch
        adhoc_output = self.adhoc_mlp(adhoc_features)
        
        # Concatenate all features
        combined = torch.cat([cnn_output, bilstm_output, adhoc_output], dim=1)
        
        # Final classification
        output = self.classifier(combined)
        
        return output