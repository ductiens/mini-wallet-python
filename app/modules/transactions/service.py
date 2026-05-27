from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.transactions import repository
from app.common.exceptions import NotFoundException

async def get_transaction_by_id(db: AsyncIOMotorDatabase, transaction_id: str) -> dict:
    """Get transaction details by ID. Raises NotFoundException if not found."""
    txn = await repository.get_transaction_by_id(db, transaction_id)
    if not txn:
        raise NotFoundException(
            message=f"Transaction with ID '{transaction_id}' not found",
            error_code="TRANSACTION_NOT_FOUND"
        )
    return txn

async def list_transactions(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 100) -> List[dict]:
    """Retrieve list of transactions from storage."""
    return await repository.list_transactions(db, skip=skip, limit=limit)
