import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None

    async def connect(self):
        try:
            logger.info("Connecting to MongoDB...")
            # For Atlas, setting standard timeouts is helpful
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                uuidRepresentation="standard"
            )
            self.db = self.client[settings.DATABASE_NAME]
            # Ping database to verify connection
            await self.client.admin.command("ping")
            logger.info("Connected to MongoDB successfully!")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e

    async def close(self):
        if self.client:
            logger.info("Closing MongoDB connection...")
            self.client.close()
            logger.info("MongoDB connection closed.")

db_manager = DatabaseManager()

def get_db():
    return db_manager.db
