from collections import Counter
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
        topic_assignments = self.query(
            q={"topic_id": ObjectId(topic_id)},
            projection=["document_id", "document_date", "topic_label", "topic_start_date", "topic_end_date"],
            sort_order=[("document_date", -1)]
        )
        topic_assignments = list(topic_assignments)
        for ta in topic_assignments:
            ta["document_id"] = str(ta.pop("document_id"))
        return topic_assignments

    def get_article_assignment(self, article_id: str) -> Dict:
        article_assignment = self._collection.find_one({"document_id": ObjectId(article_id)})
        if article_assignment:
            for field in ["_id", "document_id", "topic_id"]:
                article_assignment[field] = str(article_assignment.pop(field))
        return article_assignment

    def search_topic_assignments(
            self, topic_start_date: str, topic_end_date: str, skip_noise_topics: bool = True,
    ):
        q = {"topic_start_date": topic_start_date, "topic_end_date": topic_end_date}
        if skip_noise_topics:
            q["topic_index"] = {"$ne": -1}
        return self.query(q)

    def get_trending_topics(self, topic_start_date: str, topic_end_date: str):
        topic_assignments = self.search_topic_assignments(topic_start_date, topic_end_date)
        topic_ids = [
            (str(topic["topic_id"]), topic["topic_label"]) for topic in topic_assignments
        ]
        topic_counts = Counter(topic_ids)
        top_pct = 0.1
        trending_topics_counts = topic_counts.most_common(int(len(topic_counts) * top_pct))
        return [
            {
                "topic_id": topic_id,
                "topic_label": topic_label,
                "num_articles": num_articles,
            }
            for (topic_id, topic_label), num_articles in trending_topics_counts
        ]

    def delete_topic_assignments(self, topic_id: str) -> bool:
        result = self._collection.delete_many({"topic_id": ObjectId(topic_id)})
        return result.deleted_count > 0
