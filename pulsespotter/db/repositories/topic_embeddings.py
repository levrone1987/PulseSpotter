from typing import Optional, Dict, List

from bson import ObjectId
from pymongo.collection import Collection

from pulsespotter.db.collections import TOPIC_ASSIGNMENTS_COLLECTION
from pulsespotter.db.repositories.base import BaseRepository


class TopicEmbeddingsRepository(BaseRepository):
    def __init__(self, environment: str = "development"):
        super().__init__(environment)
        self._collection = self._db[TOPIC_ASSIGNMENTS_COLLECTION]

    @property
    def collection(self) -> Collection:
        return self._collection

    def get_by_topic_id(self, topic_id: str) -> Optional[Dict]:
        embedding = self._collection.find_one({"_id": ObjectId(topic_id)})
        if embedding:
            embedding["_id"] = str(embedding["_id"])
        return embedding

    def get_by_topic_ids(self, topic_ids: List[str]) -> Dict:
        q = {"_id": {"$in": topic_ids}}
        response = self.query(q)
        return {str(r["_id"]): r["embedding"] for r in response}

    def delete_embedding(self, topic_id: str) -> bool:
        result = self._collection.delete_one({"_id": ObjectId(topic_id)})
        return result.deleted_count > 0
