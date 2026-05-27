import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.transactions import repository as txn_repo
from app.modules.risk import repository as risk_repo

logger = logging.getLogger(__name__)

async def fetch_transaction_context(db: AsyncIOMotorDatabase, transaction_id: str) -> Optional[dict]:
    """Retrieve transaction records to serve as context for the risk investigator agent."""
    try:
        return await txn_repo.get_transaction_by_id(db, transaction_id)
    except Exception as e:
        logger.error(f"Error fetching transaction context: {e}")
        return None

async def fetch_prediction_context(db: AsyncIOMotorDatabase, transaction_id: str) -> Optional[dict]:
    """Retrieve prediction model details to serve as risk context for the agent."""
    try:
        return await risk_repo.get_prediction_by_transaction_id(db, transaction_id)
    except Exception as e:
        logger.error(f"Error fetching prediction context: {e}")
        return None

async def fetch_features_context(db: AsyncIOMotorDatabase, transaction_id: str) -> Optional[dict]:
    """Retrieve engineered features context for the risk investigator agent."""
    try:
        return await db.features.find_one({"transaction_id": transaction_id})
    except Exception as e:
        logger.error(f"Error fetching features context: {e}")
        return None
