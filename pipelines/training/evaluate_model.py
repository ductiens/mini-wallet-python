import os
import json
import logging
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def generate_model_report(metrics_file: str, report_file: str):
    """Load JSON metrics and compile a structured model performance evaluation report."""
    logger.info("Generating model evaluation report...")
    
    if not os.path.exists(metrics_file):
        logger.warning(f"Metrics file not found at {metrics_file}. Using default placeholders.")
        metrics = {
            "model_version": "v1.0.0",
            "trained_at": "N/A",
            "dataset_size": 0,
            "metrics": {
                "logistic_regression": {"precision": 0.0, "recall": 0.0, "f1_score": 0.0, "roc_auc": 0.0},
                "random_forest": {"precision": 0.0, "recall": 0.0, "f1_score": 0.0, "roc_auc": 0.0}
            }
        }
    else:
        with open(metrics_file, "r", encoding="utf-8") as f:
            metrics = json.load(f)
            
    m_version = metrics.get("model_version", "v1.0.0")
    trained_at = metrics.get("trained_at", "N/A")
    d_size = metrics.get("dataset_size", 0)
    
    lr = metrics["metrics"]["logistic_regression"]
    rf = metrics["metrics"]["random_forest"]
    
    report_content = f"""# Model Evaluation Report

Generated automatically by the model training & evaluation pipeline.

## Metadata
- **Model Version**: `{m_version}`
- **Trained At**: `{trained_at}`
- **Dataset Size**: {d_size:,} records

## Champion Model
- **Algorithm**: `RandomForestClassifier` (Selected for its high recall and robustness to class imbalance)
- **F1 Score**: {rf['f1_score']:.4f}
- **Precision**: {rf['precision']:.4f}
- **Recall**: {rf['recall']:.4f}
- **ROC AUC**: {rf['roc_auc']:.4f}

## Baseline Model Comparison
We compared our Random Forest Classifier champion with a simple Logistic Regression baseline.

| Model / Algorithm | Precision | Recall | F1-Score | ROC AUC |
| --- | --- | --- | --- | --- |
| **Logistic Regression (Baseline)** | {lr['precision']:.4f} | {lr['recall']:.4f} | {lr['f1_score']:.4f} | {lr['roc_auc']:.4f} |
| **Random Forest (Champion)** | {rf['precision']:.4f} | {rf['recall']:.4f} | {rf['f1_score']:.4f} | {rf['roc_auc']:.4f} |

## Metrics Interpretation
- **Precision**: Measures how many transactions flagged as fraud are actually fraud. Essential to minimize false alarms and reduce customer friction.
- **Recall**: Measures what percentage of actual fraud cases the model successfully catches. High recall is critical in Fintech to prevent financial losses.
- **ROC AUC**: Summarizes model capability of distinguishing between legitimate and fraudulent transactions.
"""

    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    logger.info(f"Model report compiled and written to {report_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate model and generate report")
    parser.add_argument("--metrics_file", type=str, default="reports/metrics.json", help="Path to input metrics json file")
    parser.add_argument("--report_file", type=str, default="reports/model_report.md", help="Path to output report markdown file")
    args = parser.parse_args()
    
    generate_model_report(args.metrics_file, args.report_file)
