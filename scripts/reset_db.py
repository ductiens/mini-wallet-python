import logging
from pymongo import MongoClient
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def reset_database():
    """Purge Fintech FraudOps collections from MongoDB to enable clean pipeline runs."""
    logger.info(f"Connecting to MongoDB database '{settings.DATABASE_NAME}' for resetting...")
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    collections_to_drop = [
        "transactions",
        "features",
        "predictions",
        "model_runs",
        "agent_reports"
    ]
    
    for coll in collections_to_drop:
        logger.info(f"Dropping collection '{coll}'...")
        db[coll].drop()
        
    logger.info("Database reset completed successfully! All designated collections dropped.")
    client.close()

if __name__ == "__main__":
    reset_database()
