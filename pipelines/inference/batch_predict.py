import os
import json
import joblib
import logging
import argparse
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def map_probability_to_risk_level(probability: float) -> str:
    """Standard risk level mapping rules."""
    if probability < 0.3:
        return "LOW"
    elif probability < 0.7:
        return "MEDIUM"
    else:
        return "HIGH"

def map_risk_level_to_action(risk_level: str) -> str:
    """Standard recommended action mapping rules."""
    if risk_level == "LOW":
        return "APPROVE"
    elif risk_level == "MEDIUM":
        return "MANUAL_REVIEW"
    elif risk_level == "HIGH":
        return "BLOCK"
    return "MANUAL_REVIEW"

def batch_prediction(features_file: str, model_file: str, columns_file: str, output_file: str):
    """Execute batch inference using the champion model and export predictions."""
    logger.info("Starting batch prediction...")
    
    if not os.path.exists(features_file):
        logger.warning(f"Features file not found at {features_file}. Falling back to sample features...")
        features_file = "data/features/paysim_features.csv"
        
    if not os.path.exists(model_file):
        logger.error(f"Champion model not found at {model_file}. Please train the model first.")
        # Gracefully exit or mock
        return False
        
    # Load model and features list
    model = joblib.load(model_file)
    with open(columns_file, "r", encoding="utf-8") as f:
        feature_cols = json.load(f)
        
    df = pd.read_csv(features_file)
    
    # Verify transaction_id exists
    if "transaction_id" not in df.columns:
        raise ValueError("Missing 'transaction_id' column in features dataset.")
        
    # Align features
    X = df[feature_cols].fillna(0)
    
    # Run prediction
    logger.info(f"Predicting on {len(df)} transactions...")
    probs = model.predict_proba(X)[:, 1]
    labels = model.predict(X)
    
    # Build predictions df
    preds_df = pd.DataFrame({
        "transaction_id": df["transaction_id"],
        "fraud_probability": probs,
        "predicted_label": labels
    })
    
    # Map risk levels and recommended actions
    preds_df["risk_level"] = preds_df["fraud_probability"].apply(map_probability_to_risk_level)
    preds_df["recommended_action"] = preds_df["risk_level"].apply(map_risk_level_to_action)
    preds_df["model_version"] = "v1.0.0"
    preds_df["created_at"] = pd.Timestamp.now().isoformat() + "Z"
    
    # Export predictions CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    preds_df.to_csv(output_file, index=False)
    logger.info(f"Batch predictions successfully saved to {output_file} with shape {preds_df.shape}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run offline batch prediction")
    parser.add_argument("--features_file", type=str, default="data/features/paysim_features.csv", help="Path to features CSV file")
    parser.add_argument("--model_file", type=str, default="models/fraud_model_v1.joblib", help="Path to trained model joblib file")
    parser.add_argument("--columns_file", type=str, default="models/feature_columns.json", help="Path to feature columns json file")
    parser.add_argument("--output_file", type=str, default="data/processed/predictions.csv", help="Path to save predictions CSV file")
    args = parser.parse_args()
    
    batch_prediction(args.features_file, args.model_file, args.columns_file, args.output_file)
