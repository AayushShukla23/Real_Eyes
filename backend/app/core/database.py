import motor.motor_asyncio
from typing import Optional
from app.core.config import settings
from app.core.logging import logger


class DatabaseManager:
    """Async MongoDB Connection Manager using Motor."""

    def __init__(self):
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.db = None

    async def connect(self) -> None:
        """Connect to MongoDB on startup."""
        logger.info("Connecting to MongoDB Atlas...")
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000  # 5-second connection timeout
            )
            self.db = self.client[settings.MONGODB_DB_NAME]
            # Ping database to verify connection
            await self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB database: '{settings.MONGODB_DB_NAME}'")
        except Exception as e:
            logger.warning(
                f"MongoDB connection failed: {e}. "
                "Running in memory-only mode (reports won't persist)."
            )
            self.db = None

    async def disconnect(self) -> None:
        """Close MongoDB connection on shutdown."""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection.")


# Global Database Instance
db_manager = DatabaseManager()


def get_database():
    """Dependency helper to get the database collection."""
    return db_manager.db