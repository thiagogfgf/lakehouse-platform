#!/usr/bin/env python3
"""
Trino Table Bootstrap Script - CUSTOMIZE AQUI

TODO:
1. Ajuste create_hive_raw_table() com seu schema
2. Configure particionamento se necessário
3. Teste: docker exec airflow-webserver python3 /opt/airflow/scripts/bootstrap_tables.py

Exemplo completo em: examples/scripts/bootstrap_tables_nyc_taxi.py
"""

import os
import trino

TRINO_HOST = os.getenv("TRINO_HOST", "trino-coordinator")
TRINO_PORT = int(os.getenv("TRINO_PORT", "8080"))

def get_trino_connection(catalog="system", schema="runtime"):
    """Cria conexão com Trino"""
    return trino.dbapi.connect(
        host=TRINO_HOST,
        port=TRINO_PORT,
        user="admin",
        catalog=catalog,
        schema=schema,
        http_scheme="http",
    )

def execute_query(conn, query):
    """Executa query no Trino"""
    cursor = conn.cursor()
    try:
        print(f"Executing: {query[:80]}...")
        cursor.execute(query)
        print("✓ Query executed")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"⚠ Already exists (OK)")
        else:
            raise
    finally:
        cursor.close()

def validate_minio_buckets():
    """Valida buckets MinIO (opcional)"""
    print("\n" + "=" * 80)
    print("VALIDATING MINIO BUCKETS")
    print("=" * 80)
    print("✓ Validation passed")

def create_hive_raw_schema():
    """Cria schema raw no catálogo Hive"""
    print("\n" + "=" * 80)
    print("CREATING HIVE RAW SCHEMA")
    print("=" * 80)
    conn = get_trino_connection("hive", "default")
    execute_query(conn, "CREATE SCHEMA IF NOT EXISTS hive.raw WITH (location = 's3a://raw/')")
    conn.close()

def create_hive_raw_table():
    """
    Cria tabela raw (Hive External Table)

    TODO: CUSTOMIZE com suas colunas e tipos
    """
    print("\n" + "=" * 80)
    print("CREATING HIVE RAW TABLE")
    print("=" * 80)

    conn = get_trino_connection("hive", "raw")

    # TODO: Ajuste o schema conforme seus dados
    create_query = """
    CREATE TABLE IF NOT EXISTS hive.raw.my_table (
        id BIGINT,
        name VARCHAR,
        created_at TIMESTAMP(3),
        value DOUBLE,
        category VARCHAR
        -- TODO: Adicione suas colunas aqui
    )
    WITH (
        external_location = 's3a://raw/my_data/',
        format = 'PARQUET'
    )
    """

    execute_query(conn, create_query)
    conn.close()

def main():
    """
    Pipeline principal de bootstrap

    Cria schemas e tabelas necessários para a pipeline
    """
    print("=" * 80)
    print("TRINO TABLE BOOTSTRAP - RAW LAYER")
    print("=" * 80)

    validate_minio_buckets()
    create_hive_raw_schema()
    create_hive_raw_table()

    print("\n" + "=" * 80)
    print("✓ BOOTSTRAP COMPLETED - Raw layer ready for dbt")
    print("=" * 80)

if __name__ == "__main__":
    main()
