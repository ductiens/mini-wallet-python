from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_db
from app.modules.transactions import service
from app.modules.transactions.schema import TransactionResponse
from app.common.response import success_response
from typing import List

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=None)
async def list_transactions(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max items to retrieve"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retrieve all transactions from Kaggle PaySim imported dataset with pagination."""
    txns = await service.list_transactions(db, skip=skip, limit=limit)
    # Convert MongoDB _id to string or filter fields if necessary in the service
    formatted_txns = []
    for t in txns:
        # Avoid returning _id to client or convert to str
        t_copy = dict(t)
        if "_id" in t_copy:
            t_copy["_id"] = str(t_copy["_id"])
        formatted_txns.append(t_copy)
    return success_response(data=formatted_txns, message="Transactions retrieved successfully")

@router.get("/{transaction_id}", response_model=None)
async def get_transaction(
    transaction_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retrieve transaction details by transaction_id."""
    txn = await service.get_transaction_by_id(db, transaction_id)
    t_copy = dict(txn)
    if "_id" in t_copy:
        t_copy["_id"] = str(t_copy["_id"])
    return success_response(data=t_copy, message="Transaction retrieved successfully")
