import os
import pandas as pd
from pipelines.processing.feature_engineering import run_feature_engineering

def test_feature_engineering_pipeline():
    """Test feature engineering logic on the sample CSV file."""
    input_file = "data/sample/paysim_sample.csv"
    output_file = "data/features/paysim_features_test.csv"
    
    # Run the feature engineering pipeline
    features_df = run_feature_engineering(input_file, output_file)
    
    # Assert output exists and is a valid DataFrame
    assert isinstance(features_df, pd.DataFrame)
    assert os.path.exists(output_file)
    
    # Verify engineered columns exist
    expected_cols = [
        "transaction_id", "amount_log", "balance_diff_orig", "balance_diff_dest",
        "orig_balance_error", "dest_balance_error", "origin_balance_zero_after_txn",
        "is_merchant_dest", "type_TRANSFER", "type_CASH_OUT", "type_PAYMENT"
    ]
    for col in expected_cols:
        assert col in features_df.columns
        
    # Check mathematical logic on first payment row
    # Row 0 values: type=PAYMENT, amount=9839.64, oldbalanceOrg=170136.0, newbalanceOrig=160296.36, nameDest=M1979787155
    row0 = features_df.iloc[0]
    
    assert row0["type_PAYMENT"] == 1
    assert row0["type_TRANSFER"] == 0
    assert row0["is_merchant_dest"] == 1 # Destination name M1979787155 starts with M
    
    # orig_balance_error = old_balance_orig - amount - new_balance_orig
    # 170136.0 - 9839.64 - 160296.36 = 0.0
    assert abs(row0["orig_balance_error"]) < 1e-5
    
    # Clean up test output file
    if os.path.exists(output_file):
        os.remove(output_file)
