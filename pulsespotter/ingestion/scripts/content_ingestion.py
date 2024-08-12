import argparse
from copy import deepcopy
from datetime import datetime
from pulsespotter.ingestion.scrape_configs import SCRAPE_CONFIGS
from pulsespotter.config import *

from pulsespotter.utils.logging_utils import get_logger


def parse_input_date(input_date: str):
    try:
        return datetime.strptime(input_date, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date: '{input_date}'. Must be in format YYYY-MM-DD.")


def build_scraper(scraper_params: dict):
    scraper_params_ = deepcopy(scraper_params)
    scraper_class = scraper_params_.pop("scraper_class", None)
    if not scraper_class:
        return None
    params_cls = scraper_class.config_schema()
    params = params_cls(**scraper_params_)
    return scraper_class(params)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Content ingestion script.")
    parser.add_argument(
        "--start-date", type=parse_input_date, required=True, help="Start date in the format YYYY-MM-DD."
    )
    parser.add_argument(
        "--end-date", type=parse_input_date, required=True, help="End date in the format YYYY-MM-DD."
    )
    parser.add_argument(
        "--site-name", type=str, required=True, help="Name of the site."
    )
    parser.add_argument(
        "--page-limit", type=int, default=15, help="Limit of pages to process (default is 15)."
    )
    args = parser.parse_args()

    logger = get_logger(__name__)
    logger.info("Environment vars:")
    logger.info(f"{PROJECT_DIR=}")
    logger.info(f"{MONGO_HOST=}")
    logger.info(f"{DEV_DATABASE=}")
    logger.info(f"{OPENAI_API_KEY=}")
    logger.info(f"{ZENROWS_API_KEY=}")
    logger.info(f"{ENVIRONMENT=}")
    logger.info(50 * "-")

    logger.info("Initialising script with following parameters:")
    logger.info(f"Start Date: {args.start_date}")
    logger.info(f"End Date: {args.end_date}")
    logger.info(f"Site Name: {args.site_name}")
    logger.info(f"Page Limit: {args.page_limit}")
    logger.info(50 * "-")

    scraper_params = SCRAPE_CONFIGS.get(args.site_name)
    if not scraper_params.get("enabled", False):
        logger.info(f"Site {args.site_name} is disabled through configurations or is not supported.")
        exit()

    scraper = build_scraper(scraper_params)
    if not scraper:
        logger.info(f"Missing `scraper_class` from {args.site_name} scrape configs.")
        exit()

    logger.info("Process started ...")
    scraper.run_between(args.start_date, args.end_date, args.page_limit)
    logger.info("Process finished successfully!")