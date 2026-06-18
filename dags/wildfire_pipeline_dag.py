from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "vishnu",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="wildfire_risk_pipeline",
    description="Hourly ingestion + transformation pipeline for wildfire risk and air quality",
    default_args=default_args,
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["wildfire", "etl", "dbt", "snowflake"],
) as dag:

    ingest_task = BashOperator(
        task_id="ingest_weather_and_air_quality",
        bash_command="python /opt/airflow/ingestion/ingest.py",
    )

    dbt_run_task = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/wildfire_dbt && dbt run --profiles-dir /opt/airflow/.dbt",
    )

    dbt_test_task = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/wildfire_dbt && dbt test --profiles-dir /opt/airflow/.dbt",
    )

    ingest_task >> dbt_run_task >> dbt_test_task
