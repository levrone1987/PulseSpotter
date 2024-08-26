from typing import Optional, Dict, List

from bson import ObjectId
from pymongo.collection import Collection

from pulsespotter.db.collections import ARTICLES_VECTORS_COLLECTION
from pulsespotter.db.repositories.base import BaseRepository


class ArticlesVectorsRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self._collection = self._db[ARTICLES_VECTORS_COLLECTION]

    @property
    def collection(self) -> Collection:
        return self._collection

    def add(self, article_id: str, vector_id: str):
        return self.collection.insert_one({
            "_id": ObjectId(article_id),
            "vector_id": vector_id,
        })

    def batch_add(self, article_ids: List[str], vector_ids: List[str]):
        payload = [
            {"_id": ObjectId(article_id), "vector_id": vector_id}
            for article_id, vector_id in zip(article_ids, vector_ids)
        ]
        return self.collection.insert_many(payload)

    def get(self, article_id: str) -> Optional[Dict]:
        response = self._collection.find_one({"_id": ObjectId(article_id)})
        if response:
            response["_id"] = str(response["_id"])
        return response

    def batch_get(self, article_ids: List[str]) -> List[Dict]:
        article_oids = [ObjectId(article_id) for article_id in article_ids]
        return self.query(q={"_id": {"$in": article_oids}})

    def delete(self, article_id: str) -> bool:
        result = self._collection.delete_one({"_id": ObjectId(article_id)})
        return result.deleted_count > 0
