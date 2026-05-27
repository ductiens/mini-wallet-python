import os
import uuid
import logging
import pandas as pd
from pymongo import MongoClient
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def seed_sample_data(sample_csv: str):
    """Seed sample data from CSV to transactions and generate predictions for testing."""
    logger.info("Initializing MongoDB client for seeding sample data...")
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    if not os.path.exists(sample_csv):
        raise FileNotFoundError(f"Sample data CSV not found at {sample_csv}. Please create it first.")
        
    logger.info(f"Loading sample data from {sample_csv}...")
    df = pd.read_csv(sample_csv)
    
    # 1. Clean columns
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
    
    # Generate unique transaction_ids
    txns = []
    preds = []
    
    logger.info("Generating transactions and prediction records...")
    for idx, row in df.iterrows():
        txn_id = f"txn_seed_{idx:04d}_{uuid.uuid4().hex[:8]}"
        is_fraud_val = int(row.get("is_fraud", 0))
        
        # Build transaction doc
        txn_doc = {
            "transaction_id": txn_id,
            "step": int(row.get("step", 1)),
            "type": str(row.get("type", "PAYMENT")),
            "amount": float(row.get("amount", 0.0)),
            "name_orig": str(row.get("name_orig", "")),
            "old_balance_orig": float(row.get("old_balance_orig", 0.0)),
            "new_balance_orig": float(row.get("new_balance_orig", 0.0)),
            "name_dest": str(row.get("name_dest", "")),
            "old_balance_dest": float(row.get("old_balance_dest", 0.0)),
            "new_balance_dest": float(row.get("new_balance_dest", 0.0)),
            "is_fraud": is_fraud_val,
            "is_flagged_fraud": int(row.get("is_flagged_fraud", 0)),
            "isFraud": is_fraud_val,  # Support both naming conventions for compatibility
            "isFlaggedFraud": int(row.get("is_flagged_fraud", 0)),
            "created_at": pd.Timestamp.now().isoformat() + "Z"
        }
        txns.append(txn_doc)
        
        # Build prediction doc
        prob = 0.95 if is_fraud_val == 1 else 0.05
        # Add intermediate case for one record to test medium risk
        if idx == 4:
            prob = 0.45
            
        risk_level = "LOW"
        action = "APPROVE"
        if prob >= 0.7:
            risk_level = "HIGH"
            action = "BLOCK"
        elif prob >= 0.3:
            risk_level = "MEDIUM"
            action = "MANUAL_REVIEW"
            
        pred_doc = {
            "transaction_id": txn_id,
            "fraud_probability": prob,
            "predicted_label": 1 if prob >= 0.5 else 0,
            "risk_level": risk_level,
            "recommended_action": action,
            "model_version": "seed_model_v1.0",
            "created_at": pd.Timestamp.now().isoformat() + "Z"
        }
        preds.append(pred_doc)
        
    # Clear collections
    logger.info("Purging old collections...")
    db.transactions.delete_many({})
    db.predictions.delete_many({})
    db.features.delete_many({})
    
    # Insert docs
    logger.info(f"Inserting {len(txns)} transactions into MongoDB...")
    db.transactions.insert_many(txns)
    
    logger.info(f"Inserting {len(preds)} mock predictions into MongoDB...")
    db.predictions.insert_many(preds)
    
    # Create indexes
    logger.info("Ensuring indexes...")
    db.transactions.create_index("transaction_id", unique=True)
    db.transactions.create_index("type")
    db.transactions.create_index("is_fraud")
    
    db.predictions.create_index("transaction_id", unique=True)
    db.predictions.create_index("risk_level")
    db.predictions.create_index("predicted_label")
    
    logger.info("Database seeding successfully completed! 10 sample transactions and predictions are ready.")
    
    # Print one example transaction_id to stdout for convenient copy-paste testing
    print(f"\nSeeding successful! Use this transaction ID to test the Risk Investigation Agent API:")
    print(f"👉 http://127.0.0.1:8000/agents/risk-investigator/{txns[2]['transaction_id']}")
    print(f"👉 http://127.0.0.1:8000/agents/risk-investigator/{txns[4]['transaction_id']} (Medium Risk)")
    
    client.close()

if __name__ == "__main__":
    seed_sample_data("data/sample/paysim_sample.csv")
