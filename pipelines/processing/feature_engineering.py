import os
import uuid
import logging
import argparse
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_feature_engineering(input_file: str, output_file: str) -> pd.DataFrame:
    """Read clean PaySim dataset and engineer advanced features for training."""
    logger.info("Executing feature engineering...")
    
    if not os.path.exists(input_file):
        logger.warning(f"Clean file not found at {input_file}. Falling back to sample dataset...")
        input_file = "data/sample/paysim_sample.csv"
        
    df = pd.read_csv(input_file)
    
    # Map camelCase to snake_case just in case we are loading raw sample data directly
    column_mapping = {
        "step": "step",
        "type": "type",
        "amount": "amount",
        "nameOrig": "name_orig",
        "oldbalanceOrg": "old_balance_orig",
        "newbalanceOrig": "new_balance_orig",
        "nameDest": "name_dest",
        "oldbalanceDest": "old_balance_dest",
        "newbalanceDest": "new_balance_dest",
        "isFraud": "is_fraud",
        "isFlaggedFraud": "is_flagged_fraud"
    }
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # 1. Assign unique transaction_id if not present
    if "transaction_id" not in df.columns:
        logger.info("Assigning unique transaction IDs...")
        df["transaction_id"] = [f"txn_{uuid.uuid4().hex[:12]}" for _ in range(len(df))]
        
    # 2. Mathematical features
    df["amount_log"] = np.log1p(df["amount"])
    
    df["balance_diff_orig"] = df["old_balance_orig"] - df["new_balance_orig"]
    df["balance_diff_dest"] = df["new_balance_dest"] - df["old_balance_dest"]
    
    # Balance errors (Standard PaySim feature engineering pattern)
    df["orig_balance_error"] = df["old_balance_orig"] - df["amount"] - df["new_balance_orig"]
    df["dest_balance_error"] = df["old_balance_dest"] + df["amount"] - df["new_balance_dest"]
    
    df["origin_balance_zero_after_txn"] = (df["new_balance_orig"] == 0.0).astype(int)
    
    # 3. Recipient type (Merchant or Customer)
    df["is_merchant_dest"] = df["name_dest"].apply(lambda x: 1 if str(x).startswith("M") else 0)
    
    # 4. One-hot encoding of Transaction Type
    txn_types = ["TRANSFER", "CASH_OUT", "PAYMENT", "CASH_IN", "DEBIT"]
    for t in txn_types:
        col_name = f"type_{t}"
        df[col_name] = (df["type"] == t).astype(int)
        
    # Export only feature columns + keys
    meta_cols = ["transaction_id", "step", "type", "name_orig", "name_dest", "is_fraud", "is_flagged_fraud"]
    feature_cols = [
        "amount", "amount_log", "old_balance_orig", "new_balance_orig", "old_balance_dest", "new_balance_dest",
        "balance_diff_orig", "balance_diff_dest", "orig_balance_error", "dest_balance_error",
        "origin_balance_zero_after_txn", "is_merchant_dest",
        "type_TRANSFER", "type_CASH_OUT", "type_PAYMENT", "type_CASH_IN", "type_DEBIT"
    ]
    
    # Filter only available columns
    all_cols = [c for c in meta_cols + feature_cols if c in df.columns]
    features_df = df[all_cols]
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    features_df.to_csv(output_file, index=False)
    logger.info(f"Engineered features exported successfully to {output_file} with shape {features_df.shape}")
    return features_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Feature Engineering on PaySim clean dataset")
    parser.add_argument("--input_file", type=str, default="data/processed/paysim_clean.csv", help="Path to input cleaned CSV file")
    parser.add_argument("--output_file", type=str, default="data/features/paysim_features.csv", help="Path to output features CSV file")
    args = parser.parse_args()
    
    run_feature_engineering(args.input_file, args.output_file)
