import uuid
from typing import Optional, Dict, List

from more_itertools import first
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from qdrant_client.http.models import PointStruct

from pulsespotter.db.collections import TOPIC_EMBEDDINGS_COLLECTION
from pulsespotter.db.repositories.base import BaseVectorRepository


class TopicEmbeddingsRepository(BaseVectorRepository):
    def __init__(self):
        super().__init__()
        self._collection_name = TOPIC_EMBEDDINGS_COLLECTION
        self._collection_info = self._client.get_collection(self.collection_name) if self.collection_exists() else None

    @property
    def collection_name(self) -> str:
        return self._collection_name

    @property
    def vector_size(self) -> int:
        return self._collection_info.config.params.vectors.size

    def recreate_collection(self, vector_size: int, distance: str):
        super().recreate_collection(vector_size, distance)
        self._client.create_payload_index(
            collection_name=self.collection_name,
            field_name="topic_id",
            field_type="keyword",
        )
        self._collection_info = self._client.get_collection(self.collection_name) if self.collection_exists() else None

    def add_embedding(self, topic_id: str, embedding):
        vector_id = str(uuid.uuid4())
        response = self._client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(id=vector_id,vector=embedding, payload={"topic_id": topic_id})],
        )
        return vector_id, response

    def batch_add_embeddings(self, topic_ids: List[str], embeddings):
        response = []
        for topic_id, embedding in zip(topic_ids, embeddings):
            vector_id, res = self.add_embedding(topic_id, embedding)
            response.append((vector_id, res))
        return response

    def get_embeddings(self, vector_ids: List[str]):
        records = self._client.retrieve(
            collection_name=self.collection_name, ids=vector_ids, with_vectors=True, with_payload=True
        )
        response = []
        for record in records:
            response.append({
                "vector_id": record.id, "topic_id": record.payload["topic_id"], "embedding": record.vector
            })
        return response

    def get_topic_embedding(self, topic_id: str) -> Optional[Dict]:
        filter_ = Filter(must=[FieldCondition(key="topic_id", match=MatchValue(value=topic_id))])
        search_results = self._client.search(
            collection_name=self.collection_name,
            query_vector=[0] * self.vector_size,
            limit=1,
            query_filter=filter_,
            with_vectors=True,
        )
        response = first(search_results, None)
        if response:
            return {"topic_id": topic_id, "vector": response.vector}

    def search_similar(self, topic_id: str, min_similarity: float = 0.8, limit: int = 5):
        topic_embedding = self.get_topic_embedding(topic_id)
        response = []
        if topic_embedding:
            similar_points = self._client.search(
                collection_name=self.collection_name,
                query_vector=topic_embedding["vector"],
                limit=limit + 1,
                score_threshold=min_similarity,
            )
            for point in similar_points:
                similar_topic_id = point.payload.get("topic_id")
                if similar_topic_id and similar_topic_id != topic_id:
                    response.append({
                        "topic_id": similar_topic_id,
                        "score": point.score,
                    })
        return response[:limit]
