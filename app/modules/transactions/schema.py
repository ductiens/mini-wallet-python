from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class TransactionResponse(BaseModel):
    """Schema representing a transaction in Fintech FraudOps Copilot (PaySim structure)."""
    transaction_id: str = Field(..., description="Unique transaction ID (generated or mapped)")
    step: int = Field(..., description="Step represents a unit of time in the real world (1 step = 1 hour)")
    type: str = Field(..., description="Type of transaction (e.g., PAYMENT, TRANSFER, CASH_OUT)")
    amount: float = Field(..., description="Amount of the transaction")
    nameOrig: str = Field(..., description="Customer who initiated the transaction")
    oldbalanceOrg: float = Field(..., description="Initial balance before the transaction")
    newbalanceOrig: float = Field(..., description="New balance after the transaction")
    nameDest: str = Field(..., description="Customer who is the recipient of the transaction")
    oldbalanceDest: float = Field(..., description="Initial balance of recipient before the transaction")
    newbalanceDest: float = Field(..., description="New balance of recipient after the transaction")
    isFraud: int = Field(..., description="Whether the transaction is fraudulent (1) or not (0)")
    isFlaggedFraud: int = Field(..., description="Whether the transaction is flagged as fraud (1) or not (0)")
    created_at: Optional[datetime] = Field(None, description="Timestamp when imported/recorded")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "transaction_id": "018fc1a3-2d2c-7b0a-8bf8-d3f3e2b2a1a0",
                "step": 1,
                "type": "TRANSFER",
                "amount": 1000000.0,
                "nameOrig": "C200000001",
                "oldbalanceOrg": 1000000.0,
                "newbalanceOrig": 0.0,
                "nameDest": "C200000002",
                "oldbalanceDest": 0.0,
                "newbalanceDest": 0.0,
                "isFraud": 1,
                "isFlaggedFraud": 0,
                "created_at": "2026-05-27T13:45:00Z"
            }
        }
