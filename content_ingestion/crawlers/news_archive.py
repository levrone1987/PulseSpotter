from urllib.parse import urljoin

import requests
from dateutil import parser
from pymongo import MongoClient, errors
from scrapy.selector import Selector

from content_ingestion.config import ZENROWS_API_KEY, WEBSITES, CRAWL_CONFIGS, MONGO_HOST, MONGO_DATABASE, \
    MONGO_COLLECTION
from core.utils.logging_utils import LoggingMeta


class NewsArchiveCrawler(metaclass=LoggingMeta):
    def __init__(
            self,
            site_name: str,
            base_url: str,
            search_url_template: str,
            request_params: dict,
            articles_pattern: str,
            date_format: str = "%Y-%m-%d",
    ):
        self._site_name = site_name
        self._base_url = base_url
        self._search_url_template = search_url_template
        self._date_format = date_format
        self._request_params = request_params
        self._articles_pattern = articles_pattern
        self.logger.info(f"Crawler ready for {self._base_url}.")

    @staticmethod
    def load(website: str):
        if website not in WEBSITES or website not in CRAWL_CONFIGS:
            raise NotImplementedError(f"Website {website} is not supported.")
        site_params = WEBSITES.get(website)
        if not site_params.get("enabled", False):
            raise ValueError(f"Website {website} not enabled.")
        base_url = site_params.get("base_url")
        crawl_configs = CRAWL_CONFIGS.get(website)
        return NewsArchiveCrawler(site_name=website, base_url=base_url, **crawl_configs)

    def crawl_articles(self, date: str):
        try:
            # establish db connection
            with MongoClient(MONGO_HOST) as mongo_client:
                self.logger.info(f"Running crawler for {self._base_url} on  {date} ...")

                db = mongo_client[MONGO_DATABASE]
                collection = db[MONGO_COLLECTION]

                # attempt to get page content
                formatted_date = parser.parse(date).strftime(self._date_format)
                search_url = self._search_url_template.format(date=formatted_date)
                params = {"url": search_url, "apikey": ZENROWS_API_KEY, **self._request_params}
                response = requests.get("https://api.zenrows.com/v1/", params=params)
                response.raise_for_status()

                # extract article urls and store into db
                sel = Selector(text=response.text)
                found_urls = sel.xpath(self._articles_pattern).getall()
                for url in found_urls:
                    full_url = urljoin(self._base_url, url)
                    if not collection.find_one({"url": full_url}):
                        collection.insert_one({"url": full_url, "visited": False, "site_name": self._site_name})
                self.logger.info(f"Successfully crawled articles from {self._base_url} on {date}.")

        except errors.PyMongoError as e:
            self.logger.error(f"MongoDB error: {e}")
        except requests.RequestException as e:
            self.logger.error(f"HTTP request error: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
