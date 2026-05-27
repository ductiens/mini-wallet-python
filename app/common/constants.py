from enum import Enum


class PaySimTransactionType(str, Enum):
    """Transaction types in the PaySim dataset."""
    TRANSFER = "TRANSFER"
    CASH_OUT = "CASH_OUT"
    CASH_IN = "CASH_IN"
    PAYMENT = "PAYMENT"
    DEBIT = "DEBIT"


class RiskLevel(str, Enum):
    """Risk levels assigned by the fraud detection model."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RecommendedAction(str, Enum):
    """Recommended actions based on risk level."""
    APPROVE = "APPROVE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    BLOCK = "BLOCK"


class ModelVersion(str, Enum):
    """Versioning for trained ML models."""
    V1 = "v1.0.0"
