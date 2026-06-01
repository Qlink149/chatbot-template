"""[BOILERPLATE] MongoDB client and connection management.

Do not modify per client.
"""
import os

from pymongo import MongoClient

from src.utils.logger_config import logger

_client = None
_db = None


def get_client():
    """Get singleton MongoDB client."""
    global _client
    if not _client:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise RuntimeError("MONGO_URI not set")
        _client = MongoClient(mongo_uri)
        logger.info("MongoDB client initialized")
    return _client


def get_db():
    """Get database connection.

    Returns:
        MongoDB database instance.
    """
    global _db
    if not _db:
        client = get_client()
        db_name = os.getenv("MONGO_DB_NAME", "chatbot")
        _db = client[db_name]
    return _db


def close_mongo():
    """Close MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")
