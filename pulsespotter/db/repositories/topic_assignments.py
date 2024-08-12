from typing import Optional, Dict, List

from bson import ObjectId
from pymongo.collection import Collection

from pulsespotter.db.collections import TOPIC_ASSIGNMENTS_COLLECTION
from pulsespotter.db.repositories.base import BaseRepository


class TopicAssignmentsRepository(BaseRepository):
    def __init__(self, environment: str = "development"):
        super().__init__(environment)
        self._collection = self._db[TOPIC_ASSIGNMENTS_COLLECTION]

    @property
    def collection(self) -> Collection:
        return self._collection

    def get_topic_assignments(self, topic_id: str) -> List[Dict]:
        return self.query(q={"topic_id": ObjectId(topic_id)})

    def get_topic_assignments_between(
            self, topic_start_date: str, topic_end_date: str, skip_noise_topics: bool = True,
    ):
        q = {"topic_start_date": topic_start_date, "topic_end_date": topic_end_date}
        if skip_noise_topics:
            q["topic_index"] = {"$ne": -1}
        return self.query(q)

    def delete_topic_assignments(self, topic_id: str) -> bool:
        result = self._collection.delete_many({"topic_id": ObjectId(topic_id)})
        return result.deleted_count > 0
