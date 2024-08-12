from pymongo import MongoClient
from pulsespotter.config import DEV_DATABASE, MONGO_HOST, ENVIRONMENT


def get_database(environment: str = "development"):
    environment = environment or ENVIRONMENT
    if environment == "development":
        db_name = DEV_DATABASE
    else:
        raise NotImplementedError(f"Database not found for {environment=}.")
    client = MongoClient(MONGO_HOST)
    db = client[db_name]
    return db
