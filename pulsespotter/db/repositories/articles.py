from typing import Optional, Dict, List

import pymongo
from bson import ObjectId
from pymongo.collection import Collection

from pulsespotter.db.collections import ARTICLES_COLLECTION
from pulsespotter.db.repositories.base import BaseRepository
from pulsespotter.ingestion.utils.parse_functions import parse_date


class ArticlesRepository(BaseRepository):
    def __init__(self, environment: str = "development"):
        super().__init__(environment)
        self._collection = self._db[ARTICLES_COLLECTION]

    @property
    def collection(self) -> Collection:
        return self._collection

    def add_article(
            self,
            url: str,
            site_name: str,
            raw_date: str,
            parsed_date: str = None,
            title: list | str = None,
            description: list | str = None,
            paragraphs: list | str = None,
            visited: bool = True,
    ):
        if not parsed_date:
            parsed_date = parse_date(raw_date)
        return self._collection.insert_one({
            "url": url,
            "site_name": site_name,
            "raw_date": raw_date,
            "parsed_date": parsed_date,
            "title": title,
            "description": description,
            "paragraphs": paragraphs,
            "visited": visited,
        })

    def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        article = self._collection.find_one({"_id": ObjectId(article_id)})
        if article:
            article["_id"] = str(article["_id"])
        return article

    def get_article_by_url(self, url: str) -> Optional[Dict]:
        article = self._collection.find_one({"url": url})
        if article:
            article["_id"] = str(article["_id"])
        return article

    def search_articles(
            self,
            phrase: str = None,
            site_name: str = None,
            start_date: str = None,
            end_date: str = None,
            limit: int = None,
            projection: List | Dict = None,
            sort: bool = False,
    ):
        q = {}
        if start_date:
            q["parsed_date"] = {"$gte": start_date}
        if end_date:
            q["parsed_date"] = {"$lte": end_date, **q.get("parsed_date", {})}
        if site_name:
            q["site_name"] = {"$eq": site_name}
        if phrase:
            q["$or"] = [
                {"title": {"$regex": phrase, "$options": "i"}},
                {"description": {"$regex": phrase, "$options": "i"}},
                {"paragraphs": {"$elemMatch": {"$regex": phrase, "$options": "i"}}}
            ]
        params = dict(q=q, limit=limit, projection=projection)
        if sort:
            params["sort_order"] = [("parsed_date", pymongo.DESCENDING), ("raw_date", pymongo.DESCENDING)]
        return self.query(**params)

    def update_article(self, article_id: str, updates: Dict) -> bool:
        result = self._collection.update_one({"_id": ObjectId(article_id)}, {"$set": updates})
        return result.modified_count > 0

    def delete_article(self, article_id: str) -> bool:
        result = self._collection.delete_one({"_id": ObjectId(article_id)})
        return result.deleted_count > 0
