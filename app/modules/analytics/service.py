import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

async def get_fraud_rate(db: AsyncIOMotorDatabase) -> dict:
    """Calculate the fraud rate over all imported transactions."""
    total = await db.transactions.count_documents({})
    fraud = await db.transactions.count_documents({"isFraud": 1})
    rate = float(fraud) / total if total > 0 else 0.0
    return {
        "total_transactions": total,
        "fraud_transactions": fraud,
        "fraud_rate": rate
    }

async def get_transaction_types(db: AsyncIOMotorDatabase) -> dict:
    """Get the distribution counts across all transaction types."""
    pipeline = [
        {"$group": {"_id": "$type", "count": {"$sum": 1}}}
    ]
    cursor = db.transactions.aggregate(pipeline)
    results = await cursor.to_list(length=100)
    
    counts = {}
    for r in results:
        t_type = r.get("_id")
        if t_type:
            counts[str(t_type)] = r.get("count", 0)
    return {"type_counts": counts}
