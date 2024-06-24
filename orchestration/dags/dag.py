from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "malek",
    "retries": 5,
    "retry_delay": timedelta(minutes=2)
}

with DAG(
    dag_id="our_first_dag_v3",
    default_args=default_args,
    description="This is our first dag",
    start_date=datetime(2024, 6, 21, 2),
    schedule_interval="@daily",
) as dag:
    task1 = BashOperator(
        task_id="first_task",
        bash_command="echo hello world, this is the first task!"
    )
    task2 = BashOperator(
        task_id="second_task",
        bash_command="echo I am the second task and will be running after task_1!"
    )
    task1.set_downstream(task2)
