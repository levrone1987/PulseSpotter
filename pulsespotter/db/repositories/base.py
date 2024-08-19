from abc import ABC, abstractmethod
from typing import List, Dict

from pymongo.collection import Collection

from pulsespotter.db.connection import get_database


class BaseRepository(ABC):
    def __init__(self, environment: str = "development"):
        self._db = get_database(environment)

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
        collection = self.collection
        documents = collection.find(q or {}, projection=projection or {})
        if sort_order:
            documents = documents.sort(sort_order)
        if limit:
            documents = documents.limit(limit)
        documents = list(documents)
        for document in documents:
            document["_id"] = str(document.pop("_id"))
        return documents
