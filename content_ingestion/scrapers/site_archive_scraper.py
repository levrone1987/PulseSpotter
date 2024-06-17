import re
from collections import deque
from urllib.parse import urljoin

import requests
from pandas import date_range
from pymongo import MongoClient, errors
from scrapy.selector import Selector

from content_ingestion.config import ZENROWS_API_KEY, MONGO_HOST, MONGO_DATABASE, MONGO_COLLECTION
from content_ingestion.data_models import SiteArchiveScraperPipelineParams
from content_ingestion.parse_utils import parse_website
from core.utils.logging_utils import LoggingMeta


class SiteArchiveScraperPipeline(metaclass=LoggingMeta):
    def __init__(self, pipeline_params: SiteArchiveScraperPipelineParams):
        self._site_name = pipeline_params.site_name
        self._base_url = pipeline_params.base_url
        self._search_url_template = pipeline_params.search_url_template
        self._crawler_request_params = pipeline_params.crawler_request_params
        self._site_elements_patterns = pipeline_params.site_elements_patterns
        self._scraper_request_params = pipeline_params.scraper_request_params
        self._scrape_patterns = pipeline_params.scrape_patterns
        self._blacklisted_urls = pipeline_params.blacklisted_urls
        self._blacklisted_url_patterns = pipeline_params.blacklisted_url_patterns
        self.logger.info(f"Crawler ready for {self._base_url}.")

    def _get_page_source(self, url: str, request_params: dict):
        params = {"url": url, "apikey": ZENROWS_API_KEY, **request_params}
        response = requests.get("https://api.zenrows.com/v1/", params=params)
        response.raise_for_status()
        return response.text

    def _find_article_urls(self, page_source: str):
        selector = Selector(text=page_source)
        articles_pattern = self._site_elements_patterns.articles_pattern
        found_urls = selector.xpath(articles_pattern).getall()
        return [urljoin(self._base_url, url) for url in found_urls]

    def _page_limit_reached(self, page_content, max_num_pages: int):
        selector = Selector(text=page_content)
        active_page_pattern = self._site_elements_patterns.active_page_pattern
        if active_page_pattern is None:
            return False
        active_page_element = selector.xpath(active_page_pattern).get()
        if active_page_element is None:
            return False
        active_page = int(selector.xpath(f"""{active_page_pattern}//text()""").get())
        return active_page > max_num_pages

    def _get_next_page(self, page_content):
        next_page_pattern = self._site_elements_patterns.next_page_pattern
        if next_page_pattern is None:
            return None
        selector = Selector(text=page_content)
        next_page_element = selector.xpath(next_page_pattern).get()
        if next_page_element is not None:
            next_page_url = selector.xpath(f"""{next_page_pattern}//a/@href""").get()
            next_page_url = urljoin(self._base_url, next_page_url)
            return next_page_url

    def _should_scrape_article(self, url):
        for blacklist_pattern in self._blacklisted_url_patterns:
            if re.search(blacklist_pattern, url):
                return False
        return True

    def run(self, start_date: str, end_date: str, max_num_pages: int):
        crawl_req_params = self._crawler_request_params.model_dump(exclude_unset=True)
        scrape_req_params = self._scraper_request_params.model_dump(exclude_unset=True)
        try:
            start_urls = []
            for date in date_range(start_date, end_date).strftime("%Y-%m-%d").tolist():
                year, month, day = date.split("-")
                search_url = self._search_url_template.format(year=year, month=month, day=day)
                start_urls.append(search_url)
            start_urls = deque(start_urls)

            with MongoClient(MONGO_HOST) as mongo_client:
                db = mongo_client[MONGO_DATABASE]
                collection = db[MONGO_COLLECTION]

                while len(start_urls) > 0:
                    self.logger.info(f"{len(start_urls)} urls left to crawl ...")
                    start_url = start_urls.popleft()
                    page_content = self._get_page_source(start_url, crawl_req_params)
                    if self._page_limit_reached(page_content, max_num_pages):
                        self.logger.info(f"Page limit reached for site: {start_url} ...")
                        continue

                    self.logger.info(f"Crawling {start_url} ...")
                    article_urls = self._find_article_urls(page_content)
                    for article_url in article_urls:
                        # check if article url already ingested
                        if not collection.find_one({"url": article_url}) and self._should_scrape_article(article_url):
                            self.logger.info(f"Extracting content from {article_url} ...")
                            article_content = self._get_page_source(article_url, scrape_req_params)
                            fields = {"url": article_url, "visited": True, "site_name": self._site_name}
                            parsed_content = parse_website(article_content, self._scrape_patterns)
                            parsed_content = {**parsed_content, **fields}
                            collection.insert_one(parsed_content)

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
