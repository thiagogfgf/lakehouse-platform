"""
DAG Template - CUSTOMIZE AQUI

TODO:
1. Renomeie para: <seu_projeto>_pipeline.py
2. Ajuste dag_id, schedule, tasks
3. Importe seus scripts de ingestão
4. Configure dependências entre tasks

Exemplo completo em: examples/dags/nyc_taxi_pipeline.py
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# TODO: Importe seu script de ingestão
# from ingest_your_data import main as ingest_main

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='my_pipeline',  # TODO: Renomeie
    default_args=default_args,
    description='Minha pipeline de dados',
    schedule_interval=None,  # TODO: Configure (ex: '0 2 * * *' para diário)
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['template'],
) as dag:

    # TODO: Adicione suas tasks aqui

    # Exemplo de task Python
    # ingest = PythonOperator(
    #     task_id='ingest_data',
    #     python_callable=ingest_main,
    # )

    # Exemplo de task Bash
    # dbt_run = BashOperator(
    #     task_id='dbt_run',
    #     bash_command='python3 /opt/airflow/scripts/run_dbt.py',
    # )

    # TODO: Defina dependências
    # ingest >> dbt_run

    pass  # Remova quando adicionar tasks
