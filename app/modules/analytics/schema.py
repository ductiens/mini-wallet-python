from pydantic import BaseModel, Field
from typing import Dict

class FraudRateResponse(BaseModel):
    """Schema representing fraud rate calculation."""
    total_transactions: int = Field(..., description="Total transactions in the database")
    fraud_transactions: int = Field(..., description="Total actual fraud transactions (isFraud = 1)")
    fraud_rate: float = Field(..., description="Ratio of fraud transactions to total transactions [0.0 - 1.0]")

class TransactionTypesResponse(BaseModel):
    """Schema representing transaction type distribution."""
    type_counts: Dict[str, int] = Field(..., description="Mapping of transaction type to total count")
