from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class PredictionResponse(BaseModel):
    """Schema representing a model prediction for a transaction."""
    transaction_id: str = Field(..., description="Unique transaction ID predicted on")
    fraud_probability: float = Field(..., description="Probability of transaction being fraudulent [0.0 - 1.0]")
    risk_level: str = Field(..., description="Assessed risk level: LOW, MEDIUM, HIGH")
    predicted_label: int = Field(..., description="Predicted class label: 1 (Fraud) or 0 (Legitimate)")
    recommended_action: str = Field(..., description="Recommended action: APPROVE, MANUAL_REVIEW, BLOCK")
    model_version: str = Field("v1.0.0", description="Version of the model that executed inference")
    created_at: datetime = Field(..., description="Timestamp of inference execution")

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "018fc1a3-2d2c-7b0a-8bf8-d3f3e2b2a1a0",
                "fraud_probability": 0.91,
                "risk_level": "HIGH",
                "predicted_label": 1,
                "recommended_action": "BLOCK",
                "model_version": "v1.0.0",
                "created_at": "2026-05-27T13:45:00Z"
            }
        }

class RiskSummaryResponse(BaseModel):
    """Schema representing a summary of transaction risks."""
    total_predictions: int = Field(..., description="Total transactions predicted")
    high_risk_count: int = Field(..., description="Number of HIGH risk transactions")
    medium_risk_count: int = Field(..., description="Number of MEDIUM risk transactions")
    low_risk_count: int = Field(..., description="Number of LOW risk transactions")
    fraud_ratio: float = Field(..., description="Ratio of fraudulent transactions based on predictions")
