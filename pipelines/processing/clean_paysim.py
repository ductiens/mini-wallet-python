import os
import logging
import argparse
import pandas as pd
from pipelines.ingestion.load_raw_csv import load_raw_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def clean_dataset(input_file: str, output_file: str) -> pd.DataFrame:
    """Cleans raw PaySim data by standardizing column names and saving as snake_case CSV."""
    logger.info("Cleaning dataset columns...")
    df = load_raw_data(input_file)
    
    # Map camelCase to snake_case
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
    
    # Rename only columns that exist
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # Save cleaned data
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    logger.info(f"Cleaned dataset saved successfully to {output_file} with shape {df.shape}")
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean raw PaySim dataset column names")
    parser.add_argument("--input_file", type=str, default="data/sample/paysim_sample.csv", help="Path to input CSV file")
    parser.add_argument("--output_file", type=str, default="data/processed/paysim_clean.csv", help="Path to output cleaned CSV file")
    args = parser.parse_args()
    
    clean_dataset(args.input_file, args.output_file)
