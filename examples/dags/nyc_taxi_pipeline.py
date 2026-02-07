"""NYC Taxi Data Pipeline"""

import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

sys.path.append('/opt/airflow/scripts')

from ingest_nyc_taxi import main as ingest_nyc_taxi_main
from bootstrap_tables import (
    validate_minio_buckets,
    create_hive_raw_schema,
    create_hive_raw_table,
)

default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='nyc_taxi_pipeline',
    default_args=default_args,
    description='NYC Taxi lakehouse pipeline',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=['lakehouse', 'nyc-taxi', 'iceberg'],
) as dag:

    validate_buckets = PythonOperator(
        task_id='validate_buckets',
        python_callable=validate_minio_buckets,
    )

    ingest_data = PythonOperator(
        task_id='ingest_nyc_taxi',
        python_callable=ingest_nyc_taxi_main,
    )

    create_hive_schema = PythonOperator(
        task_id='create_hive_raw_schema',
        python_callable=create_hive_raw_schema,
    )

    create_hive_table = PythonOperator(
        task_id='create_hive_raw_table',
        python_callable=lambda: create_hive_raw_table(
            os.getenv('NYC_TAXI_YEAR', '2023'),
            os.getenv('NYC_TAXI_MONTH', '01')
        ),
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='python3 /opt/airflow/scripts/run_dbt.py',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='python3 /opt/airflow/scripts/run_dbt_test.py',
    )

    # Dependencies: raw → dbt (staging/marts) → test
    validate_buckets >> ingest_data >> create_hive_schema >> create_hive_table >> dbt_run >> dbt_test
