import datetime
from collections import deque

from pandas import date_range

from pulsespotter.db.repositories.articles import ArticlesRepository
from pulsespotter.ingestion.utils.data_models import NewsArchiveScraperParams
from pulsespotter.ingestion.utils.parse_utils import parse_website
from pulsespotter.ingestion.scrapers.base import NewsScraper


class NewsArchiveScraper(NewsScraper):

    @staticmethod
    def config_schema():
        return NewsArchiveScraperParams

    def __init__(self, params: NewsArchiveScraperParams):
        super().__init__(params)
        self._search_url_templates = params.search_url_templates
        self._overwrite_date_if_not_exists = params.overwrite_date_if_not_exists

    def _get_start_urls(self, start_date: datetime.datetime, end_date: datetime.datetime = None):
        if end_date is None:
            dates = [start_date.strftime("%Y-%m-%d")]
        else:
            dates = date_range(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
            dates = dates.strftime("%Y-%m-%d")
        start_urls = {}
        for search_url_template in self._search_url_templates:
            for date in dates:
                year, month, day = date.split("-")
                start_url = search_url_template.format(year=year, month=month, day=day)
                start_urls[start_url] = date
        start_urls = sorted([(date, start_url) for start_url, date in start_urls.items()], reverse=True)
        return start_urls

    def _run(self, start_date: datetime.datetime, page_limit: int, end_date: datetime.datetime = None):

        self.logger.info(f"Starting scraper for {self._base_url}:")
        self.logger.info(f"start_date: {start_date}; end_date: {end_date}; page_limit: {page_limit}")
        articles_repository = ArticlesRepository()

        crawl_req_params = self._crawler_request_params.model_dump(exclude_unset=True)
        scrape_req_params = self._scraper_request_params.model_dump(exclude_unset=True)
        start_urls = deque(self._get_start_urls(start_date, end_date))

        while len(start_urls) > 0:
            self.logger.info(f"{len(start_urls)} urls left to crawl ...")
            start_url_date, start_url = start_urls.popleft()
            last_evaluated_date = start_url_date
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
                if not articles_repository.get_article_by_url(article_url) and self._should_scrape_article(article_url):
                    self.logger.info(f"Extracting content from {article_url} ...")
                    article_content = self.get_page_source(article_url, scrape_req_params)
                    parsed_content = parse_website(article_content, self._scrape_patterns)
                    if self._overwrite_date_if_not_exists:
                        parsed_content["parsed_date"] = parsed_content.get("parsed_date") or start_url_date
                        parsed_content["raw_date"] = parsed_content.get("raw_date") or start_url_date
                    if (article_date := parsed_content.get("parsed_date")) is not None:
                        date_limit_reached = article_date < start_date.strftime("%Y-%m-%d")
                    articles_repository.add_article(
                        url=article_url, site_name=self._site_name, visited=True, **parsed_content
                    )
                    last_evaluated_date = article_date
                if date_limit_reached:
                    break

            if date_limit_reached:
                self.logger.info(f"Date limit reached. Interrupting crawler for {start_url} ...")
                continue

            next_page_url = self._get_next_page(page_content)
            if next_page_url is not None:
                start_urls.appendleft((last_evaluated_date, next_page_url))
                self.logger.info(f"Visiting next page ...")

        self.logger.info(f"Successfully crawled articles from {self._base_url}.")

    def run_between(self, start_date: datetime.datetime, end_date: datetime.datetime, page_limit: int):
        self._run(start_date=start_date, end_date=end_date, page_limit=page_limit)

    def run(self, date: datetime.datetime, page_limit: int):
        self._run(start_date=date, page_limit=page_limit)
