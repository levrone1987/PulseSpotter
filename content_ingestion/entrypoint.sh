#!/usr/bin/env bash
set -e

# Initialize the database
airflow db migrate

# Create an admin user if not exists
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname Admin \
    --role Admin \
    --email admin@example.com \
    --password admin

# Include the plugins directory in PYTHONPATH
export PYTHONPATH=$AIRFLOW_HOME

# Run the web server and scheduler
exec airflow webserver & exec airflow scheduler
