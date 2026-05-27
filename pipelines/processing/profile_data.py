import os
import logging
import argparse
import pandas as pd
from pipelines.ingestion.load_raw_csv import load_raw_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def profile_dataset(input_file: str, report_file: str) -> None:
    """Analyze the dataset and save the summary profile as a Markdown report."""
    logger.info("Profiling dataset...")
    df = load_raw_data(input_file)
    
    rows, cols = df.shape
    missing_vals = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    
    # Fraud statistics (column name could be isFraud or is_fraud depending on step)
    fraud_col = "isFraud" if "isFraud" in df.columns else ("is_fraud" if "is_fraud" in df.columns else None)
    if fraud_col:
        fraud_count = int(df[fraud_col].sum())
        fraud_ratio = float(df[fraud_col].mean())
    else:
        fraud_count = 0
        fraud_ratio = 0.0
        
    type_col = "type" if "type" in df.columns else None
    type_dist = df[type_col].value_counts().to_dict() if type_col else {}
    
    # Formulate Markdown Report
    report_content = f"""# Data Profile Report

Generated automatically by the data profiling pipeline.

## Dataset Summary
- **Source File**: `{input_file}`
- **Total Records**: {rows:,}
- **Total Features**: {cols}
- **Missing Values**: {missing_vals:,}
- **Duplicate Rows**: {duplicate_rows:,}
- **Actual Fraud Transactions**: {fraud_count:,}
- **Fraud Ratio**: {fraud_ratio * 100:.4f}%

## Transaction Type Distribution
| Transaction Type | Volume | Percentage |
| --- | --- | --- |
"""
    for t_type, count in type_dist.items():
        pct = (count / rows) * 100
        report_content += f"| {t_type} | {count:,} | {pct:.2f}% |\n"
        
    report_content += """
## Column Distribution & Data Types
| Column | Non-Null Count | Dtype |
| --- | --- | --- |
"""
    for col in df.columns:
        report_content += f"| {col} | {df[col].notnull().sum():,} | {df[col].dtype} |\n"

    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    logger.info(f"Data Profile Report saved to {report_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Profile PaySim dataset")
    parser.add_argument("--input_file", type=str, default="data/sample/paysim_sample.csv", help="Path to input CSV file")
    parser.add_argument("--report_file", type=str, default="reports/data_profile.md", help="Path to output report file")
    args = parser.parse_args()
    
    profile_dataset(args.input_file, args.report_file)
