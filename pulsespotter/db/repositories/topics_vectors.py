from typing import Optional, Dict, List

from bson import ObjectId
from pymongo.collection import Collection

from pulsespotter.db.collections import TOPICS_VECTORS_COLLECTION
from pulsespotter.db.repositories.base import BaseRepository


class TopicsVectorsRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self._collection = self._db[TOPICS_VECTORS_COLLECTION]

    @property
    def collection(self) -> Collection:
        return self._collection

    def add(self, topic_id: str, vector_id: str):
        return self.collection.insert_one({
            "_id": ObjectId(topic_id),
            "vector_id": vector_id,
        })

    def batch_add(self, topic_ids: List[str], vector_ids: List[str]):
        payload = [
            {"_id": ObjectId(topic_id), "vector_id": vector_id}
            for topic_id, vector_id in zip(topic_ids, vector_ids)
        ]
        return self.collection.insert_many(payload)

    def get(self, topic_id: str) -> Optional[Dict]:
        response = self._collection.find_one({"_id": ObjectId(topic_id)})
        if response:
            response["_id"] = str(response["_id"])
        return response

    def batch_get(self, topic_ids: List[str]) -> List[Dict]:
        topic_oids = [ObjectId(topic_id) for topic_id in topic_ids]
        return self.query(q={"_id": {"$in": topic_oids}})

    def delete(self, topic_id: str) -> bool:
        result = self._collection.delete_one({"_id": ObjectId(topic_id)})
        return result.deleted_count > 0
