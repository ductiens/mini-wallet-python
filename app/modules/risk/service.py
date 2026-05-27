from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.risk import repository
from app.common.exceptions import NotFoundException

def map_probability_to_risk_level(probability: float) -> str:
    """
    Map a fraud probability float [0.0, 1.0] to a risk category.
    Rules:
    - fraud_probability < 0.3 => LOW
    - 0.3 <= fraud_probability < 0.7 => MEDIUM
    - fraud_probability >= 0.7 => HIGH
    """
    if probability < 0.3:
        return "LOW"
    elif probability < 0.7:
        return "MEDIUM"
    else:
        return "HIGH"

def map_risk_level_to_action(risk_level: str) -> str:
    """
    Map a risk level category to a system recommended action.
    Rules:
    - LOW => APPROVE
    - MEDIUM => MANUAL_REVIEW
    - HIGH => BLOCK
    """
    if risk_level == "LOW":
        return "APPROVE"
    elif risk_level == "MEDIUM":
        return "MANUAL_REVIEW"
    elif risk_level == "HIGH":
        return "BLOCK"
    else:
        return "MANUAL_REVIEW"

async def get_prediction(db: AsyncIOMotorDatabase, transaction_id: str) -> dict:
    """Get prediction for a transaction. Raises NotFoundException if not found."""
    pred = await repository.get_prediction_by_transaction_id(db, transaction_id)
    if not pred:
        raise NotFoundException(
            message=f"Prediction for transaction ID '{transaction_id}' not found",
            error_code="PREDICTION_NOT_FOUND"
        )
    return pred

async def list_high_risk_transactions(db: AsyncIOMotorDatabase, limit: int = 100) -> List[dict]:
    """List high risk predictions sorted by severity."""
    return await repository.list_high_risk_predictions(db, limit=limit)

async def get_risk_summary(db: AsyncIOMotorDatabase) -> dict:
    """Retrieve database-aggregated prediction risk summary statistics."""
    return await repository.get_risk_summary(db)
