from copy import deepcopy
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from logger import DummyLogger
from settings import PIPELINE_PARAMS

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
logger = DummyLogger()


# Define the DAG
with DAG(
    'daily_ingestion',
    default_args=default_args,
    description='Daily ingestion DAG',
    schedule_interval="0 10 * * *",
    start_date=datetime(2024, 6, 25),
    tags=['ingestion'],
    catchup=False,
) as ingestion_dag:

    def run_ingestion(site_name, **context):
        execution_date = context.get("logical_date")
        scraper_params = PIPELINE_PARAMS.get(site_name)

        if not scraper_params or not scraper_params.get("enabled", False):
            raise ValueError(
                f"Error loading configurations for {site_name=}. "
                "Reason: Either configuration is missing or "
                "the site scraper is disabled through configs"
            )

        scraper_params_ = deepcopy(scraper_params)
        scraper_class = scraper_params_.pop("scraper_class", None)
        if not scraper_class:
            raise ValueError(
                f"Missing `scraper_class` from {site_name} scrape configs."
            )

        params_cls = scraper_class.config_schema()
        params = params_cls(**scraper_params_)
        scraper = scraper_class(params)
        execution_date = datetime(year=execution_date.year, month=execution_date.month, day=execution_date.day)
        yesterday = execution_date - timedelta(days=1)
        scraper.run(yesterday, page_limit=16)


    tasks = [
        PythonOperator(
            task_id=f"{site_name}_ingestion_task",
            python_callable=run_ingestion,
            op_kwargs={"site_name": site_name},
            provide_context=True,
        )
        for site_name, scraper_params in PIPELINE_PARAMS.items()
        if scraper_params.get("enabled", False)
    ]

    tasks
