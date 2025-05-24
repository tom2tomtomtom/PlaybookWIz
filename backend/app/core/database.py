"""
Database configuration and connection management.

This module handles database connections for PostgreSQL, MongoDB, and Redis.
"""

import logging
from typing import AsyncGenerator

import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

# PostgreSQL Database
# Convert sync URL to async URL for SQLAlchemy
async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    async_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create sync engine for migrations
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create sync session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create database tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


# MongoDB Database
class MongoDB:
    """MongoDB connection manager."""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database = None
    
    async def connect(self):
        """Connect to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.database = self.client.get_default_database()
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_collection(self, name: str):
        """Get MongoDB collection."""
        if not self.database:
            raise RuntimeError("MongoDB not connected")
        return self.database[name]


# MongoDB instance
mongodb = MongoDB()


async def get_mongodb():
    """Get MongoDB database."""
    if not mongodb.database:
        await mongodb.connect()
    return mongodb.database


# Redis Database
class RedisDB:
    """Redis connection manager."""
    
    def __init__(self):
        self.redis: redis.Redis = None
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            
            # Test connection
            await self.redis.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Error connecting to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str):
        """Get value from Redis."""
        if not self.redis:
            await self.connect()
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, ex: int = None):
        """Set value in Redis."""
        if not self.redis:
            await self.connect()
        return await self.redis.set(key, value, ex=ex)
    
    async def delete(self, key: str):
        """Delete key from Redis."""
        if not self.redis:
            await self.connect()
        return await self.redis.delete(key)
    
    async def exists(self, key: str):
        """Check if key exists in Redis."""
        if not self.redis:
            await self.connect()
        return await self.redis.exists(key)


# Redis instance
redis_db = RedisDB()


async def get_redis():
    """Get Redis connection."""
    if not redis_db.redis:
        await redis_db.connect()
    return redis_db.redis
