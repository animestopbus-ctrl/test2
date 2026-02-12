"""MongoDB Client Wrapper for LastPerson07Bot

This module provides a robust MongoDB connection with error handling,
reconnection logic, and helper methods for database operations.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config.config import LASTPERSON07_MONGODB_URI, LASTPERSON07_DB_NAME

# Setup logging
logger = logging.getLogger(__name__)

class LastPerson07DatabaseClient:
    """MongoDB client wrapper with connection management."""
    
    def __init__(self):
        """Initialize database client."""
        self.uri = LASTPERSON07_MONGODB_URI
        self.db_name = LASTPERSON07_DB_NAME
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.is_connected = False
        self._connection_lock = asyncio.Lock()
        
    async def connect(self) -> bool:
        """Establish connection to MongoDB."""
        async with self._connection_lock:
            if self.is_connected and self.client is not None:
                return True
                
            try:
                self.client = AsyncIOMotorClient(
                    self.uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=5000
                )
                
                # Test connection
                await self.client.admin.command('ping')
                self.database = self.client.get_default_database()
                self.is_connected = True
                
                logger.info("Successfully connected to MongoDB")
                return True
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                self.is_connected = False
                self.client = None
                return False
            except Exception as e:
                logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
                self.is_connected = False
                self.client = None
                return False
    
    async def disconnect(self) -> None:
        """Close database connection."""
        if self.client is not None:
            self.client.close()
            self.is_connected = False
            logger.info("Disconnected from MongoDB")
    
    async def ensure_connection(self) -> bool:
        """Ensure database connection is active."""
        if not self.is_connected:
            return await self.connect()
        return True
    
    async def get_collection(self, collection_name: str):
        """Get a collection instance with connection check."""
        if await self.ensure_connection():
            return self.database[collection_name]
        return None
    
    async def create_indexes(self) -> None:
        """Create necessary indexes for optimal performance."""
        if not await self.ensure_connection():
            return
            
        try:
            # Users collection indexes (no _id index since it's automatically unique)
            users = self.database.users
            await users.create_index("username")
            await users.create_index("tier")
            await users.create_index("banned")
            
            # Schedules collection indexes
            schedules = self.database.schedules
            await schedules.create_index([("channel_id", 1), ("interval", 1)])
            await schedules.create_index("last_post_time")
            
            # API URLs collection index
            api_urls = self.database.api_urls
            await api_urls.create_index("url", unique=True)
            
            # Bot settings collection index
            bot_settings = self.database.bot_settings
            await bot_settings.create_index("_id", unique=True)
            
            logger.info("Created database indexes successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
    
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> Optional[Any]:
        """Insert a single document."""
        coll = await self.get_collection(collection)
        if coll is None:
            return None
            
        try:
            result = await coll.insert_one(document)
            logger.debug(f"Inserted document in {collection} with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting document in {collection}: {str(e)}")
            return None
    
    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document."""
        coll = await self.get_collection(collection)
        if coll is None:
            return None
            
        try:
            document = await coll.find_one(query)
            return document
        except Exception as e:
            logger.error(f"Error finding document in {collection}: {str(e)}")
            return None
    
    async def find_many(self, collection: str, query: Dict[str, Any], 
                       limit: int = 100, skip: int = 0) -> list:
        """Find multiple documents."""
        coll = await self.get_collection(collection)
        if coll is None:
            return []
            
        try:
            cursor = coll.find(query).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            return documents
        except Exception as e:
            logger.error(f"Error finding documents in {collection}: {str(e)}")
            return []
    
    async def update_one(self, collection: str, query: Dict[str, Any], 
                        update: Dict[str, Any], upsert: bool = False) -> bool:
        """Update a single document."""
        coll = await self.get_collection(collection)
        if coll is None:
            return False
            
        try:
            await coll.update_one(query, update, upsert=upsert)
            logger.debug(f"Updated document in {collection} with query: {query}")
            return True
        except Exception as e:
            logger.error(f"Error updating document in {collection}: {str(e)}")
            return False
    
    async def update_many(self, collection: str, query: Dict[str, Any], 
                         update: Dict[str, Any]) -> bool:
        """Update multiple documents."""
        coll = await self.get_collection(collection)
        if coll is None:
            return False
            
        try:
            result = await coll.update_many(query, update)
            logger.debug(f"Updated {result.modified_count} documents in {collection}")
            return True
        except Exception as e:
            logger.error(f"Error updating documents in {collection}: {str(e)}")
            return False
    
    async def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete a single document."""
        coll = await self.get_collection(collection)
        if coll is None:
            return False
            
        try:
            await coll.delete_one(query)
            logger.debug(f"Deleted document from {collection} with query: {query}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document from {collection}: {str(e)}")
            return False
    
    async def count_documents(self, collection: str, query: Dict[str, Any]) -> int:
        """Count documents matching query."""
        coll = await self.get_collection(collection)
        if coll is None:
            return 0
            
        try:
            count = await coll.count_documents(query)
            return count
        except Exception as e:
            logger.error(f"Error counting documents in {collection}: {str(e)}")
            return 0
    
    async def aggregate(self, collection: str, pipeline: list) -> list:
        """Execute aggregation pipeline."""
        coll = await self.get_collection(collection)
        if coll is None:
            return []
            
        try:
            cursor = coll.aggregate(pipeline)
            results = await cursor.to_list(length=1000)
            return results
        except Exception as e:
            logger.error(f"Error aggregating in {collection}: {str(e)}")
            return []

# Global database client instance
lastperson07_db_client = LastPerson07DatabaseClient()
