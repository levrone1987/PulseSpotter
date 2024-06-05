from collections import deque
from urllib.parse import urljoin

import requests
from pymongo import MongoClient, errors
from scrapy.selector import Selector

from content_ingestion.config import ZENROWS_API_KEY, MONGO_HOST, MONGO_DATABASE, MONGO_COLLECTION
from content_ingestion.utils import parse_website
from core.utils.logging_utils import LoggingMeta


class SiteScraper(metaclass=LoggingMeta):
    def __init__(
            self,
            site_name: str,
            base_url: str,
            crawl_configs: dict,
            parse_configs: dict,
            blacklisted_urls: list,
    ):
        self._site_name = site_name
        self._base_url = base_url
        self._crawl_configs = crawl_configs
        self._parse_configs = parse_configs
        self._blacklisted_urls = blacklisted_urls
        self.logger.info(f"Crawler ready for {self._base_url}.")

    def _find_start_urls(self, page_source: str):
        selector = Selector(text=page_source)
        topics_urls_pattern = self._crawl_configs["extract_patterns"]["topics_urls_pattern"]
        found_urls = selector.xpath(topics_urls_pattern).getall()
        found_urls = [urljoin(self._base_url, url) for url in found_urls]
        found_urls = [url for url in found_urls if url.startswith(self._base_url)]
        found_urls = [url for url in found_urls if url not in self._blacklisted_urls]
        return found_urls

    def _should_crawl_website(self, page_source: str):
        selector = Selector(text=page_source)
        must_exist_pattern = self._crawl_configs["extract_patterns"]["must_exist_pattern"]
        if selector.xpath(must_exist_pattern).get() is None:
            return False
        return True

    def _find_article_urls(self, page_source: str):
        selector = Selector(text=page_source)
        articles_pattern = self._crawl_configs["extract_patterns"]["articles_pattern"]
        found_urls = selector.xpath(articles_pattern).getall()
        return [urljoin(self._base_url, url) for url in found_urls]

    def _get_page_source(self, url: str, request_params: dict):
        params = {"url": url, "apikey": ZENROWS_API_KEY, **request_params}
        response = requests.get("https://api.zenrows.com/v1/", params=params)
        response.raise_for_status()
        return response.text

    def crawl_articles(self, max_num_pages: int):
        crawl_configs = self._crawl_configs
        parse_configs = self._parse_configs
        try:
            # extract start urls from the first page
            first_page_content = self._get_page_source(self._base_url, crawl_configs.get("request_params", {}))
            start_urls = deque(self._find_start_urls(first_page_content))
            self.logger.info(f"Found {len(start_urls)} start URLs ...")

            with MongoClient(MONGO_HOST) as mongo_client:
                db = mongo_client[MONGO_DATABASE]
                collection = db[MONGO_COLLECTION]

                while len(start_urls) > 0:
                    self.logger.info(f"{len(start_urls)} urls left to crawl ...")

                    # check if page has relevant structure for scraping articles
                    start_url = start_urls.popleft()
                    page_content = self._get_page_source(start_url, crawl_configs.get("request_params", {}))
                    if not self._should_crawl_website(page_content):
                        self.logger.info(f"Skipping {start_url} ...")
                        continue

                    selector = Selector(text=page_content)
                    active_page_pattern = crawl_configs["extract_patterns"]["active_page_pattern"]
                    active_page_element = selector.xpath(active_page_pattern).get()
                    if active_page_element is not None:
                        active_page = int(selector.xpath(f"""{active_page_pattern}//text()""").get())
                        if active_page > max_num_pages:
                            continue

                    self.logger.info(f"Crawling {start_url} ...")
                    article_urls = self._find_article_urls(page_content)
                    for article_url in article_urls:
                        # check if article url already ingested
                        if not collection.find_one({"url": article_url}):
                            self.logger.info(f"Extracting content from {article_url} ...")
                            article_content = self._get_page_source(article_url, parse_configs.get("request_params", {}))
                            parsed_content = parse_website(article_content, parse_configs.get("extract_patterns", {}))
                            fields = {"url": article_url, "visited": True, "site_name": self._site_name}
                            parsed_content_not_empty = any([x is not None for x in parsed_content.values()])
                            if parsed_content_not_empty:
                                fields = {**fields, **parsed_content}
                            collection.insert_one(fields)

                    next_page_pattern = crawl_configs["extract_patterns"]["next_page_pattern"]
                    next_page_element = selector.xpath(next_page_pattern).get()
                    if next_page_element is not None:
                        next_page_url = selector.xpath(f"""{next_page_pattern}//a/@href""").get()
                        next_page_url = urljoin(self._base_url, next_page_url)
                        start_urls.appendleft(next_page_url)
                        self.logger.info(f"Visiting next page ...")

            self.logger.info(f"Successfully crawled articles from {self._base_url}.")

        except errors.PyMongoError as e:
            self.logger.error(f"MongoDB error: {e}")
        except requests.RequestException as e:
            self.logger.error(f"HTTP request error: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
