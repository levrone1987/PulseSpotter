from pandas import date_range
from content_ingestion.crawlers.site_archive_crawler import SiteArchiveCrawler
from content_ingestion.config import WEBSITES


if __name__ == '__main__':

    start_date = "2024-05-25"
    end_date = "2024-05-25"
    websites_to_crawl = [site_key for site_key, site_params in WEBSITES.items() if site_params.get("enabled")]

    for site_key in websites_to_crawl:
        crawler = SiteArchiveCrawler.load(site_key)
        for date in date_range(start_date, end_date).strftime("%Y-%m-%d").tolist():
            crawler.crawl_articles(date)
