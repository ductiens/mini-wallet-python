import logging
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.transactions.schema import TransactionResponse

logger = logging.getLogger(__name__)

async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create indexes for performance and lookups on transaction_id."""
    try:
        await db.transactions.create_index("transaction_id", unique=True)
        await db.transactions.create_index("type")
        await db.transactions.create_index("isFraud")
        logger.info("Transactions collection indexes verified/created.")
    except Exception as e:
        logger.error(f"Error ensuring transactions indexes: {e}")

async def get_transaction_by_id(db: AsyncIOMotorDatabase, transaction_id: str) -> Optional[dict]:
    """Retrieve a single transaction by its unique transaction_id."""
    return await db.transactions.find_one({"transaction_id": transaction_id})

async def list_transactions(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 100) -> List[dict]:
    """List transactions with pagination, sorted by step (time) or created_at descending."""
    cursor = db.transactions.find().skip(skip).limit(limit).sort("step", -1)
    return await cursor.to_list(length=limit)
