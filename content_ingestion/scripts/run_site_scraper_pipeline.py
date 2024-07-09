from datetime import datetime

from content_ingestion.config import PIPELINE_PARAMS
from content_ingestion.data_models import NewsScraperParams
from content_ingestion.scrapers.site_scraper import NewsSiteScraper

if __name__ == '__main__':

    # fixme: currently on hold
    #  to costly and not too much news coverage
    site_name = "faz"
    until_date = datetime(year=2024, month=6, day=4)
    params = PIPELINE_PARAMS.get(site_name)

    if params.get("enabled", False):
        pipeline_params = NewsScraperParams(**params)
        pipeline = NewsSiteScraper(pipeline_params)
        pipeline.run(date=until_date, page_limit=15)
