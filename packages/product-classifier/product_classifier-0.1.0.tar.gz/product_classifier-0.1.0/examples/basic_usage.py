"""
Basic usage example for CNN-BiLSTM Classifier
"""

from product_classifier import CNNBiLSTMInference

def main():
    # Example 1: Load model from HuggingFace Hub
    print("Loading model from HuggingFace Hub...")
    model = CNNBiLSTMInference.from_pretrained("turgutguvercin/product-classifier-v1")
    
    # Example 2: Single prediction
    print("\n" + "="*50)
    print("Single Prediction Example")
    print("="*50)
    
    text = "Yataş Bedding BAMBU Yorgan (%20 Bambu) 300 Gr."
    prediction = model.predict(text, top_k=3)
    
    print(f"Text: {text}")
    print("Top 3 predictions:")
    for i, (label, score) in enumerate(prediction, 1):
        print(f"  {i}. {label}: {score:.4f}")
    
    # Example 3: Batch prediction
    print("\n" + "="*50)
    print("Batch Prediction Example")
    print("="*50)
    
    texts = [
        "Yataş Bedding BAMBU Yorgan (%20 Bambu) 300 Gr.",
        "Arji Ev ve Ofis Çalışma Sandalyesi Bilgisayar Koltuğu",
        "Siveno Sivrisinek ve Kene Kovucu Sprey Losyon",
        "Cocowiss Chocolate Sütlü Çikolata Sos 300 gr"
    ]
    
    predictions = model.predict(texts, top_k=2)
    
    for i, (text, pred) in enumerate(zip(texts, predictions)):
        print(f"\nText {i+1}: {text}")
        print("Predictions:")
        for j, (label, score) in enumerate(pred, 1):
            print(f"  {j}. {label}: {score:.4f}")
    
    # Example 4: Model information
    print("\n" + "="*50)
    print("Model Information")
    print("="*50)
    
    info = model.get_model_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # Example 5: Feature extraction
    print("\n" + "="*50)
    print("Feature Extraction Example")
    print("="*50)
    
    from product_classifier import AdHocFeatureExtractor
    
    feature_extractor = AdHocFeatureExtractor()
    sample_text = "Yataş Bedding BAMBU Yorgan (%20 Bambu) 300 Gr."
    features = feature_extractor.extract_features([sample_text])
    
    print(f"Text: {sample_text}")
    print(f"Extracted features: {features[0]}")
    print(f"Number of features: {len(features[0])}")
    
    # Show feature descriptions
    print("\nFeature descriptions:")
    print(feature_extractor.describe_features())

if __name__ == "__main__":
    main()