from datetime import datetime
from content_ingestion.config import PIPELINE_PARAMS
from content_ingestion.logging import DummyLogger
from content_ingestion.utils.module_import import import_class


if __name__ == '__main__':

    today = datetime.now()
    page_limit = 1
    logger = DummyLogger()

    for site_name, scraper_params in PIPELINE_PARAMS.items():
        scraper_class_path = scraper_params.pop("scraper_class", None)
        if not scraper_class_path:
            logger.info(f"Missing `scraper_class` from {site_name} scrape configs.")
            continue

        scraper_cls = import_class(scraper_class_path)
        params_cls = scraper_cls.config_schema()
        params = params_cls(**scraper_params)
        scraper = scraper_cls(params)

        logger.info(site_name)
        scraper.run(today, page_limit)
