import requests
from pymongo import MongoClient, errors
from tqdm import tqdm

from content_ingestion.config import MONGO_HOST, MONGO_DATABASE, DOCS_COLLECTION

if __name__ == '__main__':

    try:
        with MongoClient(MONGO_HOST) as mongo_client:
            db = mongo_client[MONGO_DATABASE]
            docs_collection = db[DOCS_COLLECTION]

            # query = {"site_name": "handelsblatt", "paragraphs": {"$exists": False}}
            query = {"site_name": "handelsblatt", "full_text": {"$exists": True}}
            cursor = docs_collection.find(query)
            num_docs = docs_collection.count_documents(query)
            pbar = tqdm(total=num_docs)

            for doc in cursor:

                # full_text = doc["full_text"]
                # paragraphs = full_text.split(".")
                # paragraphs = [p + "." for p in paragraphs]

                docs_collection.update_one(
                    filter={"_id": doc["_id"]},
                    update={
                        # "$set": {"paragraphs": paragraphs},
                        "$unset": {"full_text": ""},
                    },
                )
                pbar.update(1)

    except errors.PyMongoError as e:
        print(f"MongoDB error: {e}")
    except requests.RequestException as e:
        print(f"HTTP request error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
