#!/usr/bin/env python3
"""
Template de Ingestão de Dados

Customize este arquivo para sua fonte de dados.
Renomeie para: ingest_<seu_dado>.py
"""

import os
import boto3
import pandas as pd
from datetime import datetime

# Configuração MinIO/S3
S3_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'http://minio:9000')
S3_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID', 'minioadmin')
S3_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'minioadmin')

def extract_data():
    """
    CUSTOMIZE AQUI: Extrai dados da sua fonte

    Exemplos:
    - API REST: requests.get()
    - Database: pd.read_sql()
    - CSV/Excel: pd.read_csv() / pd.read_excel()
    - Cloud Storage: boto3, gcs, azure
    """

    # Exemplo 1: API
    # import requests
    # response = requests.get('https://api.example.com/data')
    # df = pd.DataFrame(response.json())

    # Exemplo 2: PostgreSQL
    # import psycopg2
    # conn = psycopg2.connect(host='...', database='...', user='...', password='...')
    # df = pd.read_sql("SELECT * FROM my_table", conn)

    # Exemplo 3: CSV local
    # df = pd.read_csv('/path/to/data.csv')

    # Por enquanto, retorna dados de exemplo
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'value': [100, 200, 300],
        'created_at': [datetime.now()] * 3
    })

    return df

def transform_data(df):
    """
    OPCIONAL: Transformações básicas antes de salvar
    (geralmente, deixe transformações para o dbt)
    """
    # Exemplo: remover duplicatas
    df = df.drop_duplicates(subset=['id'])

    # Exemplo: filtrar dados inválidos
    df = df[df['value'] > 0]

    return df

def load_to_s3(df, bucket='raw', prefix='my_data'):
    """
    Salva DataFrame no MinIO (S3)

    Args:
        df: DataFrame com os dados
        bucket: Nome do bucket S3
        prefix: Prefixo do caminho (pasta)
    """
    s3 = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY
    )

    # Gerar caminho particionado por ano/mês
    now = datetime.now()
    year = now.year
    month = str(now.month).zfill(2)

    # Caminho: bucket/prefix/year=YYYY/month=MM/data_YYYYMMDD_HHMMSS.parquet
    s3_key = f"{prefix}/year={year}/month={month}/data_{now.strftime('%Y%m%d_%H%M%S')}.parquet"

    # Salvar localmente primeiro
    local_path = '/tmp/data.parquet'
    df.to_parquet(local_path, index=False, engine='pyarrow')

    # Upload para S3
    s3.upload_file(local_path, bucket, s3_key)

    print(f"✓ {len(df)} registros salvos em s3://{bucket}/{s3_key}")

    return s3_key

def main():
    """
    Pipeline principal: Extract → Transform → Load
    """
    print("=" * 60)
    print("INICIANDO INGESTÃO DE DADOS")
    print("=" * 60)

    # 1. Extrair
    print("\n1. Extraindo dados...")
    df = extract_data()
    print(f"   ✓ {len(df)} registros extraídos")

    # 2. Transformar (opcional)
    print("\n2. Transformando dados...")
    df = transform_data(df)
    print(f"   ✓ {len(df)} registros após transformação")

    # 3. Carregar
    print("\n3. Carregando para S3...")
    s3_key = load_to_s3(df, bucket='raw', prefix='my_data')

    print("\n" + "=" * 60)
    print("✓ INGESTÃO CONCLUÍDA")
    print("=" * 60)

if __name__ == "__main__":
    main()
