import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import logging
import pandas as pd
from pymongo import MongoClient
from app.config import settings
from app.modules.agents.service import generate_key_signals, generate_explanation
from app.modules.risk.service import map_probability_to_risk_level, map_risk_level_to_action

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def import_data(clean_file: str, features_file: str, predictions_file: str, metrics_file: str):
    """Import dataset CSV files and metadata to MongoDB collections."""
    logger.info("Initializing MongoDB client for data import...")
    
    # Configure robust connection arguments to handle SSL issues on Windows/Atlas
    mongo_kwargs = {
        "serverSelectionTimeoutMS": 10000,
        "uuidRepresentation": "standard"
    }
    
    try:
        import certifi
        mongo_kwargs["tlsCAFile"] = certifi.where()
        logger.info("SSL/TLS CA file configured using certifi.")
    except ImportError:
        logger.warning("certifi library not found. Proceeding without specific CA file.")
        
    # Always allow invalid certs on dev/local environments to prevent SSL handshake errors
    mongo_kwargs["tlsAllowInvalidCertificates"] = True
    
    client = MongoClient(settings.MONGODB_URL, **mongo_kwargs)
    db = client[settings.DATABASE_NAME]
    
    # Keep track of transaction mapping to generate agent reports
    transactions_list = []
    predictions_map = {}
    
    # 1. Import Transactions
    if os.path.exists(clean_file):
        logger.info(f"Reading clean transactions from {clean_file}...")
        df_clean = pd.read_csv(clean_file)
        
        # Ensure transaction_id exists (might need to map or align with features)
        if "transaction_id" not in df_clean.columns:
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
        
        transactions_list = records
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
        
        for r in records:
            predictions_map[r["transaction_id"]] = r
    else:
        logger.warning(f"Predictions file not found at {predictions_file}. Skipping.")
        
    # 4. Import Model Runs (from reports/metrics.json)
    if os.path.exists(metrics_file):
        logger.info(f"Reading model training metrics from {metrics_file}...")
        with open(metrics_file, "r", encoding="utf-8") as f:
            metrics_data = json.load(f)
            
        logger.info("Importing model run to MongoDB...")
        db.model_runs.delete_many({})
        db.model_runs.insert_one(metrics_data)
        logger.info("Model runs collection imported successfully!")
    else:
        logger.warning(f"Metrics file not found at {metrics_file}. Skipping model runs import.")
        
    # 5. Generate and Import Agent Reports
    if transactions_list and predictions_map:
        logger.info("Generating Risk Investigation Agent reports for imported transactions...")
        agent_reports = []
        
        for txn in transactions_list:
            txn_id = txn["transaction_id"]
            pred = predictions_map.get(txn_id)
            if not pred:
                # Fallback prediction if not matched
                prob = 0.95 if txn.get("is_fraud") == 1 else 0.05
                pred = {
                    "transaction_id": txn_id,
                    "fraud_probability": prob,
                    "predicted_label": txn.get("is_fraud", 0),
                    "model_version": "fallback_v1"
                }
            
            prob = float(pred.get("fraud_probability", 0.0))
            risk_level = map_probability_to_risk_level(prob)
            action = map_risk_level_to_action(risk_level)
            
            # Use agent service utility to generate premium markdown signals & explanation
            signals = generate_key_signals(txn, pred)
            explanation = generate_explanation(txn, pred, signals)
            
            report_doc = {
                "transaction_id": txn_id,
                "risk_level": risk_level,
                "fraud_probability": prob,
                "key_signals": signals,
                "recommended_action": action,
                "explanation": explanation,
                "created_at": pd.Timestamp.now().isoformat() + "Z"
            }
            agent_reports.append(report_doc)
            
        logger.info(f"Importing {len(agent_reports)} generated agent reports to MongoDB...")
        db.agent_reports.delete_many({})
        db.agent_reports.insert_many(agent_reports)
        logger.info("Agent reports collection imported successfully!")
    else:
        logger.warning("Skipping Agent Reports generation due to missing transactions or predictions.")

    # 6. Create Indexes
    logger.info("Verifying and building MongoDB indexes...")
    db.transactions.create_index("transaction_id", unique=True)
    db.transactions.create_index("type")
    db.transactions.create_index("is_fraud")
    
    db.features.create_index("transaction_id", unique=True)
    
    db.predictions.create_index("transaction_id", unique=True)
    db.predictions.create_index("risk_level")
    db.predictions.create_index("predicted_label")
    db.predictions.create_index("model_version")
    
    db.model_runs.create_index("model_version")
    
    db.agent_reports.create_index("transaction_id", unique=True)
    db.agent_reports.create_index("risk_level")
    db.agent_reports.create_index("created_at")
    
    logger.info("All collection index setups completed successfully!")
    client.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Import processed transaction pipelines outputs into MongoDB")
    parser.add_argument("--clean_file", type=str, default="data/processed/paysim_clean.csv", help="Clean transaction CSV path")
    parser.add_argument("--features_file", type=str, default="data/features/paysim_features.csv", help="Features CSV path")
    parser.add_argument("--predictions_file", type=str, default="data/processed/predictions.csv", help="Predictions CSV path")
    parser.add_argument("--metrics_file", type=str, default="reports/metrics.json", help="Metrics JSON path")
    args = parser.parse_args()
    
    import_data(args.clean_file, args.features_file, args.predictions_file, args.metrics_file)
