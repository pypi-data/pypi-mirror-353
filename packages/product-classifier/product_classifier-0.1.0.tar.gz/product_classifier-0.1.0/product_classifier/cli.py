"""
Command Line Interface for CNN-BiLSTM Classifier
"""

import argparse
import json
import sys
from pathlib import Path
import pandas as pd

from .inference import CNNBiLSTMInference
from .trainer import CNNBiLSTMTrainer


def train_cli():
    """Command line interface for training"""
    parser = argparse.ArgumentParser(
        description="Train a CNN+BiLSTM classifier",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Data arguments
    parser.add_argument(
        "--data", "-d",
        type=str,
        required=True,
        help="Path to CSV file containing training data"
    )
    parser.add_argument(
        "--text-column",
        type=str,
        default="text",
        help="Name of column containing text data"
    )
    parser.add_argument(
        "--label-column", 
        type=str,
        default="label",
        help="Name of column containing labels"
    )
    
    # Output arguments
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="./cnn_bilstm_model",
        help="Directory to save trained model"
    )
    parser.add_argument(
        "--hub-repo",
        type=str,
        help="HuggingFace Hub repository to upload model (optional)"
    )
    
    # Training arguments
    parser.add_argument(
        "--batch-size",
        type=int,
        default=128,
        help="Training batch size"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=20,
        help="Number of training epochs"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.001,
        help="Learning rate"
    )
    parser.add_argument(
        "--embedding-dim",
        type=int,
        default=512,
        help="Word embedding dimension"
    )
    parser.add_argument(
        "--cnn-filters",
        type=int,
        default=128,
        help="Number of CNN filters"
    )
    parser.add_argument(
        "--lstm-hidden",
        type=int,
        default=256,
        help="LSTM hidden dimension"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=50,
        help="Maximum sequence length"
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.25,
        help="Test set size ratio"
    )
    
    # Other arguments
    parser.add_argument(
        "--config",
        type=str,
        help="Path to JSON config file (overrides command line args)"
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=["auto", "cuda", "cpu"],
        default="auto",
        help="Device to use for training"
    )
    
    args = parser.parse_args()
    
    # Load config from file if provided
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = {
            'batch_size': args.batch_size,
            'epochs': args.epochs,
            'learning_rate': args.learning_rate,
            'embedding_dim': args.embedding_dim,
            'cnn_filters': args.cnn_filters,
            'lstm_hidden': args.lstm_hidden,
            'max_length': args.max_length
        }
    
    # Load data
    print(f"Loading data from {args.data}...")
    try:
        df = pd.read_csv(args.data)
        print(f"Loaded {len(df)} samples")
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)
    
    # Validate columns
    if args.text_column not in df.columns:
        print(f"Error: Text column '{args.text_column}' not found in data")
        sys.exit(1)
    if args.label_column not in df.columns:
        print(f"Error: Label column '{args.label_column}' not found in data")
        sys.exit(1)
    
    # Initialize trainer
    trainer = CNNBiLSTMTrainer()
    
    # Train model
    print("Starting training...")
    try:
        results = trainer.train(
            df=df,
            text_column=args.text_column,
            label_column=args.label_column,
            test_size=args.test_size,
            config=config
        )
        
        print(f"Training completed! Best validation accuracy: {results['best_val_acc']:.4f}")
        
    except Exception as e:
        print(f"Error during training: {e}")
        sys.exit(1)
    
    # Save model
    print(f"Saving model to {args.output_dir}...")
    trainer.save_model(args.output_dir)
    print("Model saved successfully!")
    
    # Upload to Hub if requested
    if args.hub_repo:
        print(f"Uploading to HuggingFace Hub: {args.hub_repo}...")
        try:
            trainer.save_to_hub(args.hub_repo)
            print("Upload completed!")
        except Exception as e:
            print(f"Error uploading to Hub: {e}")


def predict_cli():
    """Command line interface for prediction"""
    parser = argparse.ArgumentParser(
        description="Make predictions with CNN+BiLSTM classifier",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Model arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--model-path",
        type=str,
        help="Path to local model directory"
    )
    group.add_argument(
        "--hub-model",
        type=str,
        help="HuggingFace Hub model name"
    )
    
    # Input arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--text",
        type=str,
        help="Single text to classify"
    )
    input_group.add_argument(
        "--file",
        type=str,
        help="Path to file containing texts (one per line)"
    )
    input_group.add_argument(
        "--csv",
        type=str,
        help="Path to CSV file containing texts"
    )
    
    # CSV-specific arguments
    parser.add_argument(
        "--text-column",
        type=str,
        default="text",
        help="Column name for text data (when using --csv)"
    )
    
    # Output arguments
    parser.add_argument(
        "--output",
        type=str,
        help="Output file to save predictions (optional)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=1,
        help="Number of top predictions to return"
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "txt"],
        default="txt",
        help="Output format"
    )
    
    # Other arguments
    parser.add_argument(
        "--device",
        type=str,
        choices=["auto", "cuda", "cpu"],
        default="auto",
        help="Device to use for inference"
    )
    
    args = parser.parse_args()
    
    # Load model
    print("Loading model...")
    try:
        if args.model_path:
            model = CNNBiLSTMInference.from_local(args.model_path)
        else:
            model = CNNBiLSTMInference.from_pretrained(args.hub_model)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)
    
    # Prepare input texts
    if args.text:
        texts = [args.text]
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f if line.strip()]
    elif args.csv:
        df = pd.read_csv(args.csv)
        if args.text_column not in df.columns:
            print(f"Error: Column '{args.text_column}' not found in CSV")
            sys.exit(1)
        texts = df[args.text_column].astype(str).tolist()
    
    print(f"Making predictions for {len(texts)} texts...")
    
    # Make predictions
    try:
        predictions = model.predict(texts, top_k=args.top_k)
        if isinstance(predictions, tuple):  # Single prediction
            predictions = [predictions]
    except Exception as e:
        print(f"Error making predictions: {e}")
        sys.exit(1)
    
    # Format and output results
    if args.format == "json":
        import json
        results = []
        for i, (text, pred) in enumerate(zip(texts, predictions)):
            result = {"text": text, "predictions": []}
            if args.top_k == 1:
                pred = [pred]
            for label, score in pred:
                result["predictions"].append({"label": label, "score": float(score)})
            results.append(result)
        
        output_str = json.dumps(results, indent=2, ensure_ascii=False)
        
    elif args.format == "csv":
        rows = []
        for text, pred in zip(texts, predictions):
            if args.top_k == 1:
                pred = [pred]
            for rank, (label, score) in enumerate(pred, 1):
                rows.append({
                    "text": text,
                    "rank": rank,
                    "label": label,
                    "score": score
                })
        
        import io
        output = io.StringIO()
        pd.DataFrame(rows).to_csv(output, index=False)
        output_str = output.getvalue()
        
    else:  # txt format
        lines = []
        for i, (text, pred) in enumerate(zip(texts, predictions)):
            lines.append(f"Text {i+1}: {text}")
            if args.top_k == 1:
                pred = [pred]
            for rank, (label, score) in enumerate(pred, 1):
                lines.append(f"  {rank}. {label}: {score:.4f}")
            lines.append("")
        output_str = "\n".join(lines)
    
    # Save or print results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_str)
        print(f"Results saved to {args.output}")
    else:
        print(output_str)


if __name__ == "__main__":
    # This allows the module to be run directly
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "train":
        sys.argv.pop(1)  # Remove "train" from args
        train_cli()
    elif len(sys.argv) > 1 and sys.argv[1] == "predict":
        sys.argv.pop(1)  # Remove "predict" from args  
        predict_cli()
    else:
        print("Usage: python -m product_classifier.cli [train|predict] [args...]")
        sys.exit(1)