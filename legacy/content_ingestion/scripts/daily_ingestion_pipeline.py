from copy import deepcopy
from datetime import datetime, timedelta
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

    today = datetime.now() - timedelta(days=1)
    page_limit = 10
    logger = DummyLogger()

    for site_name, scraper_params in PIPELINE_PARAMS.items():
        if not scraper_params.get("enabled", False):
            logger.info(f"Skipping {site_name=} - disabled through configuration.")
            continue
        scraper = build_scraper(scraper_params)
        if not scraper:
            logger.info(f"Missing `scraper_class` from {site_name} scrape configs.")
            continue
        # logger.info(f"{site_name}, {today}, {page_limit}")
        scraper.run(today, page_limit)
