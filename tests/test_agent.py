from app.modules.agents.service import generate_key_signals, generate_recommended_action, generate_explanation

def test_generate_key_signals_high_risk():
    """Test key signals generation for high risk patterns (TRANSFER, empty balance)."""
    transaction = {
        "type": "TRANSFER",
        "amount": 100000.0,
        "old_balance_orig": 100000.0,
        "new_balance_orig": 0.0,
        "name_dest": "C11111"
    }
    prediction = {
        "fraud_probability": 0.95
    }
    
    signals = generate_key_signals(transaction, prediction)
    
    assert any("high" in s.lower() or "cao" in s.lower() for s in signals)
    assert any("TRANSFER" in s for s in signals)
    assert any("rút sạch" in s or "zero" in s.lower() or "0" in s for s in signals)

def test_generate_recommended_action():
    """Test agent action mapping."""
    assert generate_recommended_action(0.95) == "BLOCK"
    assert generate_recommended_action(0.50) == "MANUAL_REVIEW"
    assert generate_recommended_action(0.05) == "APPROVE"

def test_generate_explanation_content():
    """Test markdown explanation synthesis contains critical keywords."""
    transaction = {
        "transaction_id": "txn_test_123",
        "type": "TRANSFER",
        "amount": 50000.0,
        "name_orig": "C1",
        "name_dest": "C2"
    }
    prediction = {
        "fraud_probability": 0.88
    }
    signals = ["Loại giao dịch TRANSFER.", "Mô hình đánh giá xác suất cao."]
    
    explanation = generate_explanation(transaction, prediction, signals)
    
    assert "BÁO CÁO PHÂN TÍCH RỦI RO" in explanation
    assert "txn_test_123" in explanation
    assert "TRANSFER" in explanation
    assert "50,000" in explanation
    assert "88.00%" in explanation
    assert "BLOCK" in explanation
