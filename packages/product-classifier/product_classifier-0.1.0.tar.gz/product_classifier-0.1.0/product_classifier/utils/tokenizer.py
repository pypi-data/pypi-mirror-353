from typing import Dict, List


class WordTokenizer:
    """Word-level tokenizer for inference"""
    
    def __init__(self, word2idx: Dict[str, int], idx2word: Dict[int, str], 
                 vocab_size: int, embedding_dim: int):
        self.word2idx = word2idx
        self.idx2word = idx2word
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
    
    def encode(self, text: str, max_length: int = 50) -> List[int]:
        words = str(text).lower().split()
        encoded = [self.word2idx.get(word, self.word2idx['<UNK>']) for word in words]
        
        # Truncate or pad
        if len(encoded) > max_length:
            encoded = encoded[:max_length]
        else:
            encoded = encoded + [0] * (max_length - len(encoded))
        
        return encoded