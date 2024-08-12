from datetime import datetime

from content_ingestion.config import PIPELINE_PARAMS
from content_ingestion.data_models import NewsArchiveScraperParams
from content_ingestion.scrapers.site_archive_scraper import NewsArchiveScraper


if __name__ == '__main__':

    site_name = "heise"
    start_date = datetime(year=2024, month=6, day=4)
    end_date = datetime(year=2024, month=6, day=26)
    params = PIPELINE_PARAMS.get(site_name)

    if params.get("enabled", False):
        pipeline_params = NewsArchiveScraperParams(**params)
        pipeline = NewsArchiveScraper(pipeline_params)
        pipeline.run_between(start_date=start_date, end_date=end_date, page_limit=10)
