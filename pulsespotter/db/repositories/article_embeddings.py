from typing import Optional, Dict, List

from bson import ObjectId
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
        embedding = self._collection.find_one({"_id": ObjectId(article_id)})
        if embedding:
            embedding["_id"] = str(embedding["_id"])
        return embedding

    def get_by_article_ids(self, article_ids: List[str]) -> Dict:
        q = {"_id": {"$in": article_ids}}
        response = self.query(q)
        return {str(r["_id"]): r["embedding"] for r in response}

    def delete_embedding(self, article_id: str) -> bool:
        result = self._collection.delete_one({"_id": ObjectId(article_id)})
        return result.deleted_count > 0
