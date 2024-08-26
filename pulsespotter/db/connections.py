from pymongo import MongoClient
from qdrant_client import QdrantClient

from pulsespotter.config import MONGO_DATABASE, MONGO_HOST, QDRANT_HOST, QDRANT_API_KEY

VECTOR_DB_CLIENT = QdrantClient(url=QDRANT_HOST, api_key=QDRANT_API_KEY)
MONGO_CLIENT = MongoClient(MONGO_HOST)


def get_mongo_database():
    return MONGO_CLIENT[MONGO_DATABASE]


def get_vector_database_client():
    return VECTOR_DB_CLIENT


__all__ = [
    "get_mongo_database",
    "get_vector_database_client",
]
