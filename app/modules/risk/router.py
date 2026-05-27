from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_db
from app.modules.risk import service
from app.common.response import success_response

router = APIRouter(prefix="/risk", tags=["Risk Analysis"])

@router.get("/high-risk-transactions", response_model=None)
async def list_high_risk(
    limit: int = Query(100, ge=1, le=500, description="Max high-risk records to retrieve"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retrieve transactions predicted to be high risk (fraud_probability >= 0.7) sorted by probability descending."""
    preds = await service.list_high_risk_transactions(db, limit=limit)
    formatted_preds = []
    for p in preds:
        p_copy = dict(p)
        if "_id" in p_copy:
            p_copy["_id"] = str(p_copy["_id"])
        formatted_preds.append(p_copy)
    return success_response(data=formatted_preds, message="High risk transactions retrieved successfully")

@router.get("/summary", response_model=None)
async def get_summary(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retrieve statistical summaries of total predictions, risk distributions, and predicted fraud ratio."""
    summary = await service.get_risk_summary(db)
    return success_response(data=summary, message="Risk summary statistics retrieved successfully")
