import uuid
from typing import Optional, Dict, List

from more_itertools import first
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from qdrant_client.http.models import PointStruct

from pulsespotter.db.collections import ARTICLE_EMBEDDINGS_COLLECTION
from pulsespotter.db.repositories.base import BaseVectorRepository


class ArticleEmbeddingsRepository(BaseVectorRepository):
    def __init__(self):
        super().__init__()
        self._collection_name = ARTICLE_EMBEDDINGS_COLLECTION
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
            field_name="article_id",
            field_type="keyword",
        )
        self._collection_info = self._client.get_collection(self.collection_name) if self.collection_exists() else None

    def add_embedding(self, article_id: str, embedding):
        vector_id = str(uuid.uuid4())
        response = self._client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(id=vector_id, vector=embedding, payload={"article_id": article_id})],
        )
        return vector_id, response

    def batch_add_embeddings(self, article_ids: List[str], embeddings):
        response = []
        for article_id, embedding in zip(article_ids, embeddings):
            vector_id, res = self.add_embedding(article_id, embedding)
            response.append((vector_id, res))
        return response

    def get_embeddings(self, vector_ids: List[str]):
        records = self._client.retrieve(
            collection_name=self.collection_name, ids=vector_ids, with_vectors=True, with_payload=True
        )
        response = []
        for record in records:
            response.append({
                "vector_id": record.id, "article_id": record.payload["article_id"], "embedding": record.vector
            })
        return response

    def get_article_embedding(self, article_id: str) -> Optional[Dict]:
        filter_ = Filter(must=[FieldCondition(key="article_id", match=MatchValue(value=article_id))])
        search_results = self._client.search(
            collection_name=self.collection_name,
            query_vector=[0] * self.vector_size,
            limit=1,
            query_filter=filter_,
            with_vectors=True,
        )
        response = first(search_results, None)
        if response:
            return {"article_id": article_id, "vector": response.vector}

    def check_embeddings_exist(self, article_ids: List[str]) -> List:
        response = []
        for article_id in article_ids:
            article_embedding = self.get_article_embedding(article_id)
            response.append((article_id, article_embedding is not None))
        return response

    def search_similar(self, article_id: str, min_similarity: float = 0.8, limit: int = 5):
        article_embedding = self.get_article_embedding(article_id)
        response = []
        if article_embedding:
            similar_points = self._client.search(
                collection_name=self.collection_name,
                query_vector=article_embedding["vector"],
                limit=limit + 1,
                score_threshold=min_similarity,
            )
            for point in similar_points:
                similar_article_id = point.payload.get("article_id")
                if similar_article_id and similar_article_id != article_id:
                    response.append({
                        "article_id": similar_article_id,
                        "score": point.score,
                    })
        return response[:limit]
