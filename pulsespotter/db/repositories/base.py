from abc import ABC, abstractmethod
from typing import List, Dict

from pymongo.collection import Collection
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from pulsespotter.db.connections import get_mongo_database, get_vector_database_client


class BaseRepository(ABC):
    def __init__(self):
        self._db = get_mongo_database()

    @property
    @abstractmethod
    def collection(self) -> Collection:
        pass

    def query(
            self,
            q: Dict,
            projection: Dict | List = None,
            sort_order: List = None,
            limit: int = None,
    ) -> List[Dict]:
        documents = self.collection.find(q or {}, projection=projection or {})
        if sort_order:
            documents = documents.sort(sort_order)
        if limit:
            documents = documents.limit(limit)
        documents = list(documents)
        for document in documents:
            document["_id"] = str(document.pop("_id"))
        return documents


class BaseVectorRepository(ABC):
    def __init__(self):
        self._client = get_vector_database_client()

    def collection_exists(self) -> bool:
        return self._client.collection_exists(self.collection_name)

    def recreate_collection(self, vector_size: int, distance: str):
        if self.collection_exists():
            self._client.delete_collection(self.collection_name)
        self._client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=distance,
            ),
        )

    @property
    @abstractmethod
    def collection_name(self) -> str:
        pass

    @property
    @abstractmethod
    def vector_size(self) -> int:
        pass
