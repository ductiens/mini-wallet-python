import os
import logging
import pandas as pd
from pymongo import MongoClient
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def import_data(clean_file: str, features_file: str, predictions_file: str):
    """Import dataset CSV files to MongoDB collections."""
    logger.info("Initializing MongoDB client for data import...")
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    # 1. Import Transactions
    if os.path.exists(clean_file):
        logger.info(f"Reading clean transactions from {clean_file}...")
        df_clean = pd.read_csv(clean_file)
        
        # Ensure transaction_id exists (might need to map or align with features)
        if "transaction_id" not in df_clean.columns:
            # If we don't have transaction_id, let's load it from features if available, or generate it
            if os.path.exists(features_file):
                df_feat = pd.read_csv(features_file)
                if "transaction_id" in df_feat.columns and len(df_feat) == len(df_clean):
                    df_clean["transaction_id"] = df_feat["transaction_id"]
                else:
                    df_clean["transaction_id"] = [f"txn_{i:06d}" for i in range(len(df_clean))]
            else:
                df_clean["transaction_id"] = [f"txn_{i:06d}" for i in range(len(df_clean))]
        
        # Clean data for Mongo (convert numpy types to python)
        records = df_clean.to_dict("records")
        logger.info(f"Importing {len(records)} transactions to MongoDB...")
        
        # Clear old and write new
        db.transactions.delete_many({})
        db.transactions.insert_many(records)
        logger.info("Transactions collection imported successfully!")
    else:
        logger.warning(f"Transactions clean file not found at {clean_file}. Skipping.")
        
    # 2. Import Features
    if os.path.exists(features_file):
        logger.info(f"Reading engineered features from {features_file}...")
        df_features = pd.read_csv(features_file)
        records = df_features.to_dict("records")
        logger.info(f"Importing {len(records)} features to MongoDB...")
        
        db.features.delete_many({})
        db.features.insert_many(records)
        logger.info("Features collection imported successfully!")
    else:
        logger.warning(f"Features file not found at {features_file}. Skipping.")

    # 3. Import Predictions
    if os.path.exists(predictions_file):
        logger.info(f"Reading batch predictions from {predictions_file}...")
        df_preds = pd.read_csv(predictions_file)
        records = df_preds.to_dict("records")
        logger.info(f"Importing {len(records)} predictions to MongoDB...")
        
        db.predictions.delete_many({})
        db.predictions.insert_many(records)
        logger.info("Predictions collection imported successfully!")
    else:
        logger.warning(f"Predictions file not found at {predictions_file}. Skipping.")
        
    # 4. Create Indexes
    logger.info("Verifying and building MongoDB indexes...")
    db.transactions.create_index("transaction_id", unique=True)
    db.transactions.create_index("type")
    db.transactions.create_index("is_fraud")
    
    db.features.create_index("transaction_id", unique=True)
    
    db.predictions.create_index("transaction_id", unique=True)
    db.predictions.create_index("risk_level")
    db.predictions.create_index("predicted_label")
    
    logger.info("All collection index setups completed successfully!")
    client.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Import processed transaction pipelines outputs into MongoDB")
    parser.add_argument("--clean_file", type=str, default="data/processed/paysim_clean.csv", help="Clean transaction CSV path")
    parser.add_argument("--features_file", type=str, default="data/features/paysim_features.csv", help="Features CSV path")
    parser.add_argument("--predictions_file", type=str, default="data/processed/predictions.csv", help="Predictions CSV path")
    args = parser.parse_args()
    
    import_data(args.clean_file, args.features_file, args.predictions_file)
