import logging
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create indexes for performance on predictions."""
    try:
        await db.predictions.create_index("transaction_id", unique=True)
        await db.predictions.create_index("risk_level")
        await db.predictions.create_index("predicted_label")
        logger.info("Predictions collection indexes verified/created.")
    except Exception as e:
        logger.error(f"Error ensuring predictions indexes: {e}")

async def get_prediction_by_transaction_id(db: AsyncIOMotorDatabase, transaction_id: str) -> Optional[dict]:
    """Retrieve the fraud prediction record associated with a transaction."""
    return await db.predictions.find_one({"transaction_id": transaction_id})

async def list_high_risk_predictions(db: AsyncIOMotorDatabase, limit: int = 100) -> List[dict]:
    """Retrieve high risk transaction predictions (risk_level = 'HIGH')."""
    cursor = db.predictions.find({"risk_level": "HIGH"}).limit(limit).sort("fraud_probability", -1)
    return await cursor.to_list(length=limit)

async def get_risk_summary(db: AsyncIOMotorDatabase) -> dict:
    """Aggregate predictions to build a risk level overview and fraud ratio."""
    # We can perform MongoDB aggregations
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total": {"$sum": 1},
                "high": {"$sum": {"$cond": [{"$eq": ["$risk_level", "HIGH"]}, 1, 0]}},
                "medium": {"$sum": {"$cond": [{"$eq": ["$risk_level", "MEDIUM"]}, 1, 0]}},
                "low": {"$sum": {"$cond": [{"$eq": ["$risk_level", "LOW"]}, 1, 0]}},
                "fraud_count": {"$sum": {"$cond": [{"$eq": ["$predicted_label", 1]}, 1, 0]}}
            }
        }
    ]
    cursor = db.predictions.aggregate(pipeline)
    results = await cursor.to_list(length=1)
    if not results:
        return {
            "total_predictions": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "fraud_ratio": 0.0
        }
    
    res = results[0]
    total = res.get("total", 0)
    fraud_ratio = float(res.get("fraud_count", 0)) / total if total > 0 else 0.0
    return {
        "total_predictions": total,
        "high_risk_count": res.get("high", 0),
        "medium_risk_count": res.get("medium", 0),
        "low_risk_count": res.get("low", 0),
        "fraud_ratio": fraud_ratio
    }
