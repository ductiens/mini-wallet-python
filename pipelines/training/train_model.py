import os
import json
import joblib
import logging
import argparse
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def train_models(features_file: str, model_output_path: str, columns_output_path: str, metrics_output_path: str):
    """Train machine learning models for fraud detection and export evaluation results."""
    logger.info("Training fraud detection models...")
    
    if not os.path.exists(features_file):
        logger.warning(f"Features file not found at {features_file}. Falling back to sample dataset...")
        features_file = "data/features/paysim_features.csv"
        
    df = pd.read_csv(features_file)
    
    # Identify target and features
    target_col = "is_fraud"
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in features dataset.")
        
    feature_cols = [
        "amount", "amount_log", "old_balance_orig", "new_balance_orig", "old_balance_dest", "new_balance_dest",
        "balance_diff_orig", "balance_diff_dest", "orig_balance_error", "dest_balance_error",
        "origin_balance_zero_after_txn", "is_merchant_dest",
        "type_TRANSFER", "type_CASH_OUT", "type_PAYMENT", "type_CASH_IN", "type_DEBIT"
    ]
    # Keep only features present in df
    feature_cols = [c for c in feature_cols if c in df.columns]
    
    X = df[feature_cols].fillna(0)
    y = df[target_col].fillna(0).astype(int)
    
    # Save feature columns
    os.makedirs(os.path.dirname(columns_output_path), exist_ok=True)
    with open(columns_output_path, "w", encoding="utf-8") as f:
        json.dump(feature_cols, f, indent=2)
    logger.info(f"Feature columns saved to {columns_output_path}")
    
    # Train-test split (handle very small datasets gracefully)
    test_size = 0.2 if len(df) >= 10 else 0.1
    if len(df) < 2:
        logger.warning("Dataset is too small for split. Training and evaluating on entire dataset.")
        X_train, X_test, y_train, y_test = X, X, y, y
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
    # 1. Logistic Regression Baseline
    logger.info("Fitting Logistic Regression Baseline...")
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    lr_preds = lr.predict(X_test)
    lr_probs = lr.predict_proba(X_test)[:, 1] if hasattr(lr, "predict_proba") else np.zeros(len(y_test))
    
    # 2. Random Forest Champion
    logger.info("Fitting Random Forest Classifier...")
    # Use small depth for small sample datasets to prevent overfit
    max_depth = 5 if len(df) >= 10 else 2
    rf = RandomForestClassifier(n_estimators=10, max_depth=max_depth, random_state=42)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_probs = rf.predict_proba(X_test)[:, 1]
    
    # Metrics calculation (handling single-class edge cases gracefully)
    def calc_metrics(y_true, y_pred, y_prob):
        unique_classes = len(np.unique(y_true))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        auc = float(roc_auc_score(y_true, y_prob)) if unique_classes > 1 else 0.0
        return {"precision": prec, "recall": rec, "f1_score": f1, "roc_auc": auc}
        
    lr_metrics = calc_metrics(y_test, lr_preds, lr_probs)
    rf_metrics = calc_metrics(y_test, rf_preds, rf_probs)
    
    logger.info(f"LR F1-Score: {lr_metrics['f1_score']:.4f} | RF F1-Score: {rf_metrics['f1_score']:.4f}")
    
    # Export metrics.json
    metrics_data = {
        "model_version": "v1.0.0",
        "trained_at": pd.Timestamp.now().isoformat() + "Z",
        "dataset_size": len(df),
        "metrics": {
            "logistic_regression": lr_metrics,
            "random_forest": rf_metrics
        }
    }
    
    os.makedirs(os.path.dirname(metrics_output_path), exist_ok=True)
    with open(metrics_output_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    logger.info(f"Metrics saved to {metrics_output_path}")
    
    # Save Champion Model (Random Forest)
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(rf, model_output_path)
    logger.info(f"Champion model saved to {model_output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train ML models for Fintech Fraud detection")
    parser.add_argument("--features_file", type=str, default="data/features/paysim_features.csv", help="Path to features CSV file")
    parser.add_argument("--model_output", type=str, default="models/fraud_model_v1.joblib", help="Path to save champion model")
    parser.add_argument("--columns_output", type=str, default="models/feature_columns.json", help="Path to save feature columns list")
    parser.add_argument("--metrics_output", type=str, default="reports/metrics.json", help="Path to save training metrics json")
    args = parser.parse_args()
    
    train_models(args.features_file, args.model_output, args.columns_output, args.metrics_output)
