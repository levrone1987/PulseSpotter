import datetime
import re
from abc import abstractmethod, ABC
from urllib.parse import urljoin

import requests
from scrapy import Selector
from tenacity import retry, stop_after_attempt, wait_exponential

from data_models import NewsScraperParams
from logger import LoggingMeta


class NewsScraper(ABC, metaclass=LoggingMeta):

    @staticmethod
    def config_schema():
        pass

    @staticmethod
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_page_source(url: str, zenrows_request_params: dict):
        from settings import ZENROWS_API_KEY

        params = {"url": url, "apikey": ZENROWS_API_KEY, **zenrows_request_params}
        response = requests.get("https://api.zenrows.com/v1/", params=params)
        response.raise_for_status()
        return response.text

    def __init__(self, params: NewsScraperParams):
        self._site_name = params.site_name
        self._base_url = params.base_url
        self._crawler_request_params = params.crawler_request_params
        self._site_elements_patterns = params.site_elements_patterns
        self._scraper_request_params = params.scraper_request_params
        self._scrape_patterns = params.scrape_patterns
        self._blacklisted_urls = params.blacklisted_urls
        self._blacklisted_url_patterns = params.blacklisted_url_patterns

    def _should_crawl_page(self, page_source: str):
        selector = Selector(text=page_source)
        must_exist_pattern = self._site_elements_patterns.must_exist_pattern
        if selector.xpath(must_exist_pattern).get() is None:
            return False
        return True

    def _should_scrape_article(self, url):
        for blacklist_pattern in self._blacklisted_url_patterns:
            if re.search(blacklist_pattern, url):
                return False
        return True

    def _find_article_urls(self, page_source: str):
        selector = Selector(text=page_source)
        articles_pattern = self._site_elements_patterns.articles_pattern
        found_urls = selector.xpath(articles_pattern).getall()
        return [urljoin(self._base_url, url) for url in found_urls]

    def _check_page_limit_reached(self, page_content, max_num_pages: int):
        selector = Selector(text=page_content)
        active_page_pattern = self._site_elements_patterns.active_page_pattern
        if active_page_pattern is None:
            return False
        active_page_element = selector.xpath(active_page_pattern).get()
        if active_page_element is None:
            return False
        active_page = selector.xpath(f"""{active_page_pattern}/text()""").get()
        if not active_page:
            self.logger.warning("Active page pattern provided but active page element not found.")
            return False
        active_page = int(active_page.strip())
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

    @abstractmethod
    def run(self, date: datetime.datetime, page_limit: int):
        pass

    @abstractmethod
    def run_between(self, start_date: datetime.datetime, end_date: datetime.datetime, page_limit: int):
        pass
