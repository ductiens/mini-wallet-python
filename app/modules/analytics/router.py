from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_db
from app.modules.analytics import service
from app.common.response import success_response

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/fraud-rate", response_model=None)
async def get_fraud_rate(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retrieve actual fraud occurrences rate based on ground truth labels."""
    stats = await service.get_fraud_rate(db)
    return success_response(data=stats, message="Fraud rate retrieved successfully")

@router.get("/transaction-types", response_model=None)
async def get_transaction_distribution(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retrieve total count of transactions categorized by payment type."""
    stats = await service.get_transaction_types(db)
    return success_response(data=stats, message="Transaction type distribution retrieved successfully")
