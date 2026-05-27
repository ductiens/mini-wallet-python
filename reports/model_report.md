# Model Evaluation Report

Generated automatically by the model training & evaluation pipeline.

## Metadata
- **Model Version**: `v1.0.0`
- **Trained At**: `2026-05-27T15:31:27.752953Z`
- **Dataset Size**: 10 records

## Champion Model
- **Algorithm**: `RandomForestClassifier` (Selected for its high recall and robustness to class imbalance)
- **F1 Score**: 0.0000
- **Precision**: 0.0000
- **Recall**: 0.0000
- **ROC AUC**: 0.0000

## Baseline Model Comparison
We compared our Random Forest Classifier champion with a simple Logistic Regression baseline.

| Model / Algorithm | Precision | Recall | F1-Score | ROC AUC |
| --- | --- | --- | --- | --- |
| **Logistic Regression (Baseline)** | 0.5000 | 1.0000 | 0.6667 | 1.0000 |
| **Random Forest (Champion)** | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## Metrics Interpretation
- **Precision**: Measures how many transactions flagged as fraud are actually fraud. Essential to minimize false alarms and reduce customer friction.
- **Recall**: Measures what percentage of actual fraud cases the model successfully catches. High recall is critical in Fintech to prevent financial losses.
- **ROC AUC**: Summarizes model capability of distinguishing between legitimate and fraudulent transactions.
