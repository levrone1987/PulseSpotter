from content_ingestion.config import SCRAPE_CONFIGS
from content_ingestion.scrapers.article_scraper import NewsArticleScraper


if __name__ == '__main__':

    scraper = NewsArticleScraper(SCRAPE_CONFIGS)
    scraper.run()
