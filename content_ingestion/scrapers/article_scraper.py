from copy import deepcopy

import requests
from pymongo import MongoClient, errors

from content_ingestion.config import MONGO_HOST, MONGO_DATABASE, MONGO_COLLECTION, ZENROWS_API_KEY
from content_ingestion.utils import parse_website
from core.utils.logging_utils import LoggingMeta


class NewsArticleScraper(metaclass=LoggingMeta):
    def __init__(self, scrape_configs: dict):
        self._scrape_configs = deepcopy(scrape_configs)
        self.logger.info("Scraper initialised.")

    def run(self):
        try:
            # establish db connection
            with MongoClient(MONGO_HOST) as mongo_client:
                db = mongo_client[MONGO_DATABASE]
                collection = db[MONGO_COLLECTION]
                cursor = collection.find({'visited': False})

                for doc in cursor:
                    site_name = doc['site_name']
                    site_url = doc["url"]

                    site_scrape_configs = self._scrape_configs.get(site_name, self._scrape_configs.get("default"))
                    extract_patterns = site_scrape_configs.get("extract_patterns")
                    if not extract_patterns:
                        self.logger.debug(f"Skipping due to missing configs: {site_url} ...")
                        continue

                    self.logger.info(f"Extracting page content from: {site_url} ...")

                    # retrieve page content
                    request_params = site_scrape_configs.get("request_params", {})
                    request_params["url"] = site_url
                    request_params["apikey"] = ZENROWS_API_KEY
                    response = requests.get("https://api.zenrows.com/v1/", params=request_params)
                    response.raise_for_status()

                    # parse website and ingest into db
                    parsed_content = parse_website(response.text, extract_patterns)
                    parsed_content["visited"] = True
                    collection.update_one(filter={"_id": doc["_id"]}, update={"$set": parsed_content})

        except errors.PyMongoError as e:
            self.logger.error(f"MongoDB error: {e}")
        except requests.RequestException as e:
            self.logger.error(f"HTTP request error: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
