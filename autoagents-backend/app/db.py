"""MongoDB connection helpers for AutoAgents backend."""

from __future__ import annotations

import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

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
        raise RuntimeError("MongoDB configuration missing (MONGO_URI/MONGO_DB_NAME).")

    _client = AsyncIOMotorClient(mongo_uri)
    _database = _client[db_name]


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

