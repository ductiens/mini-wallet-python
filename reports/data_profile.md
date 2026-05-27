# Data Profile Report

Generated automatically by the data profiling pipeline.

## Dataset Summary
- **Source File**: `data/sample/paysim_sample.csv`
- **Total Records**: 10
- **Total Features**: 11
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Actual Fraud Transactions**: 4
- **Fraud Ratio**: 40.0000%

## Transaction Type Distribution
| Transaction Type | Volume | Percentage |
| --- | --- | --- |
| TRANSFER | 3 | 30.00% |
| CASH_OUT | 3 | 30.00% |
| PAYMENT | 2 | 20.00% |
| DEBIT | 1 | 10.00% |
| CASH_IN | 1 | 10.00% |

## Column Distribution & Data Types
| Column | Non-Null Count | Dtype |
| --- | --- | --- |
| step | 10 | int64 |
| type | 10 | str |
| amount | 10 | float64 |
| nameOrig | 10 | str |
| oldbalanceOrg | 10 | float64 |
| newbalanceOrig | 10 | float64 |
| nameDest | 10 | str |
| oldbalanceDest | 10 | float64 |
| newbalanceDest | 10 | float64 |
| isFraud | 10 | int64 |
| isFlaggedFraud | 10 | int64 |
