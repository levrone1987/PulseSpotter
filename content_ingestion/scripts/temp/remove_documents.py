from pymongo import errors, MongoClient

from content_ingestion.config import MONGO_HOST, MONGO_DATABASE, MONGO_COLLECTION


if __name__ == '__main__':

    try:
        with MongoClient(MONGO_HOST) as mongo_client:
            db = mongo_client[MONGO_DATABASE]
            collection = db[MONGO_COLLECTION]

            query = {"site_name": "handelsblatt", "visited": False}
            cursor = collection.find(query)
            for doc in cursor:
                site_url = doc["url"]
                print(site_url)
                collection.delete_one({"_id": doc["_id"]})

    except errors.PyMongoError as e:
        print(f"MongoDB error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
