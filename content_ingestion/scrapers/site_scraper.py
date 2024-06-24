import datetime
from collections import deque
from urllib.parse import urljoin

import requests
from pymongo import MongoClient, errors
from scrapy.selector import Selector

from content_ingestion.config import MONGO_HOST, MONGO_DATABASE, MONGO_COLLECTION
from content_ingestion.data_models import NewsScraperParams
from content_ingestion.scrapers._base import NewsScraper
from content_ingestion.utils.parse_utils import parse_website


class NewsSiteScraper(NewsScraper):

    @staticmethod
    def config_schema():
        return NewsScraperParams

    def __init__(self, params: NewsScraperParams):
        super().__init__(params)

    def _get_start_urls(self, page_source: str):
        selector = Selector(text=page_source)
        topics_urls_pattern = self._site_elements_patterns.topics_urls_pattern
        found_urls = selector.xpath(topics_urls_pattern).getall()
        found_urls = [urljoin(self._base_url, url) for url in found_urls]
        found_urls = [url for url in found_urls if url.startswith(self._base_url)]
        found_urls = [url for url in found_urls if url not in self._blacklisted_urls]
        return found_urls

    def _run(self, end_date: datetime.datetime, page_limit: int):
        crawl_req_params = self._crawler_request_params.model_dump(exclude_unset=True)
        scrape_req_params = self._scraper_request_params.model_dump(exclude_unset=True)
        try:
            # extract start urls from the first page
            first_page_content = self.get_page_source(self._base_url, crawl_req_params)
            start_urls = deque(self._get_start_urls(first_page_content))
            self.logger.info(f"Found {len(start_urls)} start URLs ...")

            with MongoClient(MONGO_HOST) as mongo_client:
                db = mongo_client[MONGO_DATABASE]
                collection = db[MONGO_COLLECTION]

                while len(start_urls) > 0:
                    self.logger.info(f"{len(start_urls)} urls left to crawl ...")

                    # check if page has relevant structure for scraping articles
                    start_url = start_urls.popleft()
                    page_content = self.get_page_source(start_url, crawl_req_params)
                    if not self._should_crawl_page(page_content):
                        self.logger.info(f"Skipping {start_url} ...")
                        continue

                    if self._check_page_limit_reached(page_content, page_limit):
                        self.logger.info(f"Page limit reached for site: {start_url} ...")
                        continue

                    self.logger.info(f"Crawling {start_url} ...")
                    article_urls = self._find_article_urls(page_content)
                    date_limit_reached = False
                    for article_url in article_urls:
                        if not article_url.startswith(self._base_url):
                            continue
                        # check if article url already ingested
                        if not collection.find_one({"url": article_url}) and self._should_scrape_article(article_url):
                            self.logger.info(f"Extracting content from {article_url} ...")
                            article_content = self.get_page_source(article_url, scrape_req_params)
                            fields = {"url": article_url, "visited": True, "site_name": self._site_name}
                            parsed_content = parse_website(article_content, self._scrape_patterns)
                            if (article_date := parsed_content.get("parsed_date")) is not None:
                                date_limit_reached = article_date < end_date.strftime("%Y-%m-%d")
                            parsed_content = {**parsed_content, **fields}
                            collection.insert_one(parsed_content)
                        if date_limit_reached:
                            break

                    if date_limit_reached:
                        self.logger.info(f"Date limit reached. Interrupting crawler for {start_url} ...")
                        continue

                    next_page_url = self._get_next_page(page_content)
                    if next_page_url is not None:
                        start_urls.appendleft(next_page_url)
                        self.logger.info(f"Visiting next page ...")

            self.logger.info(f"Successfully crawled articles from {self._base_url}.")

        except errors.PyMongoError as e:
            self.logger.error(f"MongoDB error: {e}")
        except requests.RequestException as e:
            self.logger.error(f"HTTP request error: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

    def run_between(self, start_date: datetime.datetime, end_date: datetime.datetime, page_limit: int):
        pass

    def run(self, date: datetime.datetime, page_limit: int):
        self._run(end_date=date, page_limit=page_limit)
