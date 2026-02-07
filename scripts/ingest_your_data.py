#!/usr/bin/env python3
"""
Script de Ingestão - CUSTOMIZE AQUI

TODO:
1. Renomeie este arquivo para: ingest_<seu_dado>.py
2. Implemente a função extract_data() com sua fonte
3. Ajuste load_to_s3() conforme necessário
4. Teste: docker exec airflow-webserver python3 /opt/airflow/scripts/ingest_<seu_dado>.py

Exemplos completos em: examples/scripts/
Template completo em: templates/ingest_template.py
"""

import os
import boto3
import pandas as pd
from datetime import datetime

def extract_data():
    """TODO: Implementar extração dos seus dados"""
    raise NotImplementedError("Customize esta função para sua fonte de dados")

def load_to_s3(df, bucket='raw', prefix='my_data'):
    """Salva dados no MinIO (S3)"""
    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv('MINIO_ENDPOINT', 'http://minio:9000'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'minioadmin'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'minioadmin')
    )

    now = datetime.now()
    s3_key = f"{prefix}/year={now.year}/month={now.month:02d}/data.parquet"

    local_path = '/tmp/data.parquet'
    df.to_parquet(local_path, index=False)
    s3.upload_file(local_path, bucket, s3_key)

    print(f"✓ {len(df)} registros salvos em s3://{bucket}/{s3_key}")

def main():
    print("Iniciando ingestão...")
    df = extract_data()
    load_to_s3(df)
    print("✓ Concluído")

if __name__ == "__main__":
    main()
