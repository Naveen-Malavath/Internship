"""MongoDB connection helpers using Motor."""

from __future__ import annotations

import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_mongo_client: Optional[AsyncIOMotorClient] = None
_mongo_db: Optional[AsyncIOMotorDatabase] = None


def _get_mongo_uri() -> str:
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise RuntimeError("Environment variable MONGO_URI is not set")
    return uri


def _get_db_name() -> str:
    name = os.getenv("MONGO_DB_NAME")
    if not name:
        raise RuntimeError("Environment variable MONGO_DB_NAME is not set")
    return name


async def connect_to_mongo() -> None:
    """Initialise the global MongoDB client and database."""
    global _mongo_client, _mongo_db

    if _mongo_client is not None:
        return

    mongo_uri = _get_mongo_uri()
    db_name = _get_db_name()

    _mongo_client = AsyncIOMotorClient(mongo_uri)
    _mongo_db = _mongo_client[db_name]


async def close_mongo_connection() -> None:
    """Close the active MongoDB client."""
    global _mongo_client, _mongo_db

    if _mongo_client is not None:
        _mongo_client.close()

    _mongo_client = None
    _mongo_db = None


def get_database() -> AsyncIOMotorDatabase:
    """Return the active MongoDB database instance."""
    if _mongo_db is None:
        raise RuntimeError("MongoDB connection has not been initialised. Call connect_to_mongo() first.")
    return _mongo_db

