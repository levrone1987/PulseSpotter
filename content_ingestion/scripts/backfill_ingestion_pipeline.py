from copy import deepcopy
from datetime import datetime
from settings import PIPELINE_PARAMS
from logger import DummyLogger


def build_scraper(scraper_params: dict):
    scraper_params_ = deepcopy(scraper_params)
    scraper_class = scraper_params_.pop("scraper_class", None)
    if not scraper_class:
        return None
    params_cls = scraper_class.config_schema()
    params = params_cls(**scraper_params_)
    return scraper_class(params)


if __name__ == '__main__':

    start_date = datetime(year=2024, month=6, day=25)
    end_date = datetime(year=2024, month=7, day=2)
    page_limit = 15
    logger = DummyLogger()

    for site_name, scraper_params in PIPELINE_PARAMS.items():
        if site_name != "tagesspiegel":
            continue
        if not scraper_params.get("enabled", False):
            logger.info(f"Skipping {site_name=} - disabled through configuration.")
            continue
        scraper = build_scraper(scraper_params)
        if not scraper:
            logger.info(f"Missing `scraper_class` from {site_name} scrape configs.")
            continue

        logger.info(site_name)
        scraper.run_between(start_date, end_date, page_limit)
