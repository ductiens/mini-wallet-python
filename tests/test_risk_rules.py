from app.modules.risk.service import map_probability_to_risk_level, map_risk_level_to_action

def test_map_probability_to_risk_level():
    """Test mapping float probabilities to discrete risk levels."""
    # LOW risk threshold: < 0.3
    assert map_probability_to_risk_level(0.0) == "LOW"
    assert map_probability_to_risk_level(0.15) == "LOW"
    assert map_probability_to_risk_level(0.29) == "LOW"
    
    # MEDIUM risk threshold: [0.3, 0.7)
    assert map_probability_to_risk_level(0.3) == "MEDIUM"
    assert map_probability_to_risk_level(0.5) == "MEDIUM"
    assert map_probability_to_risk_level(0.69) == "MEDIUM"
    
    # HIGH risk threshold: >= 0.7
    assert map_probability_to_risk_level(0.7) == "HIGH"
    assert map_probability_to_risk_level(0.85) == "HIGH"
    assert map_probability_to_risk_level(1.0) == "HIGH"

def test_map_risk_level_to_action():
    """Test mapping risk levels to actions."""
    assert map_risk_level_to_action("LOW") == "APPROVE"
    assert map_risk_level_to_action("MEDIUM") == "MANUAL_REVIEW"
    assert map_risk_level_to_action("HIGH") == "BLOCK"
    assert map_risk_level_to_action("UNKNOWN") == "MANUAL_REVIEW"
