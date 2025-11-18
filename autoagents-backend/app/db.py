"""MongoDB connection helpers for AutoAgents backend."""

from __future__ import annotations

import logging
import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    """Initialise MongoDB client and database."""
    global _client, _database

    if _client is not None and _database is not None:
        return

    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")

    if not mongo_uri or not db_name:
        raise RuntimeError(
            "MongoDB configuration missing (MONGO_URI/MONGO_DB_NAME). "
            "Please check your .env file in the autoagents-backend directory."
        )

    # Log connection info (mask password for security)
    masked_uri = mongo_uri
    if "@" in mongo_uri:
        # Mask password in connection string
        parts = mongo_uri.split("@")
        if len(parts) == 2:
            user_pass = parts[0].split("//")[-1]
            if ":" in user_pass:
                user = user_pass.split(":")[0]
                masked_uri = mongo_uri.replace(user_pass, f"{user}:***")
    
    # Log what we're connecting to (for debugging)
    connection_host = masked_uri.split("@")[-1] if "@" in masked_uri else masked_uri
    logger.info(f"Connecting to MongoDB: {connection_host}")
    logger.info(f"Database name: {db_name}")
    
    # Warn if still using localhost
    if "localhost" in mongo_uri or "127.0.0.1" in mongo_uri:
        logger.warning(
            "WARNING: Connecting to localhost MongoDB. "
            "If you intended to use MongoDB Atlas, update MONGO_URI in your .env file."
        )

    try:
        # Increase timeout for cloud connections
        timeout_ms = 30000 if "mongodb+srv://" in mongo_uri else 5000
        _client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=timeout_ms)
        _database = _client[db_name]
        # Test the connection
        await _client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to connect to MongoDB: {error_msg}")
        
        # Provide helpful error messages
        if "localhost" in mongo_uri or "127.0.0.1" in mongo_uri:
            raise RuntimeError(
                f"MongoDB connection failed to localhost: {error_msg}\n"
                "If you're using MongoDB Atlas, update MONGO_URI in your .env file to use mongodb+srv://..."
            ) from e
        elif "mongodb+srv://" in mongo_uri:
            raise RuntimeError(
                f"MongoDB Atlas connection failed: {error_msg}\n"
                "Please check:\n"
                "1. Your internet connection\n"
                "2. MongoDB Atlas cluster is running\n"
                "3. Your IP address is whitelisted in Atlas\n"
                "4. Your credentials are correct"
            ) from e
        else:
            raise RuntimeError(f"MongoDB connection failed: {error_msg}") from e


async def close_mongo_connection() -> None:
    """Close MongoDB connection."""
    global _client, _database

    if _client is not None:
        _client.close()

    _client = None
    _database = None


def get_database() -> AsyncIOMotorDatabase:
    """Retrieve active MongoDB database."""
    if _database is None:
        raise RuntimeError("Database not initialised. Call connect_to_mongo() first.")
    return _database

