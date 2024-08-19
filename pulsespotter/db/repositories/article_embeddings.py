from typing import Optional, Dict, List

import numpy as np

from bson import ObjectId
from pulsespotter.utils.similarities import cosine_similarity
from pymongo.collection import Collection

from pulsespotter.db.collections import ARTICLE_EMBEDDINGS_COLLECTION
from pulsespotter.db.repositories.base import BaseRepository


class ArticleEmbeddingsRepository(BaseRepository):
    def __init__(self, environment: str = "development"):
        super().__init__(environment)
        self._collection = self._db[ARTICLE_EMBEDDINGS_COLLECTION]

    @property
    def collection(self) -> Collection:
        return self._collection

    def get_by_article_id(self, article_id: str) -> Optional[Dict]:
        response = self._collection.find_one({"_id": ObjectId(article_id)})
        if response:
            embedding = response["embedding"]
            return embedding

    def get_by_article_ids(self, article_ids: List[str]) -> Dict:
        article_oids = [ObjectId(article_id) for article_id in article_ids]
        q = {"_id": {"$in": article_oids}}
        response = self.query(q)
        return {str(r["_id"]): r["embedding"] for r in response}

    def similarity_search(
            self,
            src_embedding: np.array,
            target_article_ids: List,
            min_similarity: float = 0.9,
            limit: int = 5,
    ) -> List:
        # retrieve embeddings for target articles
        target_embeddings = self.get_by_article_ids(target_article_ids)
        # calculate similarity scores
        similarity_scores = []
        for article_id, embedding in target_embeddings.items():
            similarity = cosine_similarity(src_embedding, np.array(embedding))
            if similarity >= min_similarity:
                similarity_scores.append((article_id, similarity))
        similarity_scores.sort(key=lambda x: x[-1], reverse=True)
        return similarity_scores[:limit]

    def delete_embedding(self, article_id: str) -> bool:
        result = self._collection.delete_one({"_id": ObjectId(article_id)})
        return result.deleted_count > 0
