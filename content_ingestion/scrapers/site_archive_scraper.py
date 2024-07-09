import datetime
from collections import deque

import requests
from pandas import date_range
from pymongo import MongoClient, errors

from data_models import NewsArchiveScraperParams
from scrapers._base import NewsScraper
from utils.parse_utils import parse_website


class NewsArchiveScraper(NewsScraper):

    @staticmethod
    def config_schema():
        return NewsArchiveScraperParams

    def __init__(self, params: NewsArchiveScraperParams):
        super().__init__(params)
        self._search_url_template = params.search_url_template

    def _get_start_urls(self, start_date: datetime.datetime, end_date: datetime.datetime = None):
        if end_date is None:
            dates = [start_date.strftime("%Y-%m-%d")]
        else:
            dates = date_range(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
            dates = dates.strftime("%Y-%m-%d")
        start_urls = []
        for date in dates:
            year, month, day = date.split("-")
            start_urls.append(self._search_url_template.format(year=year, month=month, day=day))
        start_urls = sorted(set(start_urls), reverse=True)
        return start_urls

    def _run(self, start_date: datetime.datetime, page_limit: int, end_date: datetime.datetime = None):
        from settings import MONGO_HOST, MONGO_DATABASE, MONGO_COLLECTION

        self.logger.info(f"Starting scraper for {self._base_url}:")
        self.logger.info(f"start_date: {start_date}; end_date: {end_date}; page_limit: {page_limit}")

        crawl_req_params = self._crawler_request_params.model_dump(exclude_unset=True)
        scrape_req_params = self._scraper_request_params.model_dump(exclude_unset=True)
        try:
            start_urls = deque(self._get_start_urls(start_date, end_date))

            with MongoClient(MONGO_HOST) as mongo_client:
                db = mongo_client[MONGO_DATABASE]
                collection = db[MONGO_COLLECTION]

                while len(start_urls) > 0:
                    self.logger.info(f"{len(start_urls)} urls left to crawl ...")
                    start_url = start_urls.popleft()
                    page_content = self.get_page_source(start_url, crawl_req_params)
                    if self._check_page_limit_reached(page_content, page_limit):
                        self.logger.info(f"Page limit reached for site: {start_url} ...")
                        continue

                    self.logger.info(f"Crawling {start_url} ...")
                    article_urls = self._find_article_urls(page_content)
                    date_limit_reached = False
                    self.logger.info(f"Found {len(article_urls)} articles.")

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
                                date_limit_reached = article_date < start_date.strftime("%Y-%m-%d")
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
        self._run(start_date=start_date, end_date=end_date, page_limit=page_limit)

    def run(self, date: datetime.datetime, page_limit: int):
        self._run(start_date=date, page_limit=page_limit)
