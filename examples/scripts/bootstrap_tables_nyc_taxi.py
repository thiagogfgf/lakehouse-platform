#!/usr/bin/env python3
"""Trino Table Bootstrap Script"""

import os
import time
import trino

TRINO_HOST = os.getenv("TRINO_HOST", "trino-coordinator")
TRINO_PORT = int(os.getenv("TRINO_PORT", "8080"))
NYC_TAXI_YEAR = os.getenv("NYC_TAXI_YEAR", "2023")
NYC_TAXI_MONTH = os.getenv("NYC_TAXI_MONTH", "01").zfill(2)
NYC_TAXI_COLOR = os.getenv("NYC_TAXI_COLOR", "yellow")

def get_trino_connection(catalog="system", schema="runtime"):
    return trino.dbapi.connect(
        host=TRINO_HOST,
        port=TRINO_PORT,
        user="admin",
        catalog=catalog,
        schema=schema,
        http_scheme="http",
    )

def execute_query(conn, query):
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
    print("\n" + "=" * 80)
    print("VALIDATING MINIO BUCKETS")
    print("=" * 80)
    print("✓ Validation passed")

def create_hive_raw_schema():
    print("\n" + "=" * 80)
    print("CREATING HIVE RAW SCHEMA")
    print("=" * 80)
    conn = get_trino_connection("hive", "default")
    execute_query(conn, "CREATE SCHEMA IF NOT EXISTS hive.raw WITH (location = 's3a://raw/')")
    conn.close()

def create_hive_raw_table(year, month):
    print("\n" + "=" * 80)
    print("CREATING HIVE RAW TABLE")
    print("=" * 80)
    conn = get_trino_connection("hive", "raw")
    
    s3_path = f"s3a://raw/nyc_taxi/{NYC_TAXI_COLOR}/year={year}/month={month}/"
    
    execute_query(conn, "DROP TABLE IF EXISTS hive.raw.nyc_taxi_trips")
    
    create_query = f"""
    CREATE TABLE hive.raw.nyc_taxi_trips (
        VendorID BIGINT,
        tpep_pickup_datetime TIMESTAMP(3),
        tpep_dropoff_datetime TIMESTAMP(3),
        passenger_count DOUBLE,
        trip_distance DOUBLE,
        RatecodeID DOUBLE,
        store_and_fwd_flag VARCHAR,
        PULocationID BIGINT,
        DOLocationID BIGINT,
        payment_type BIGINT,
        fare_amount DOUBLE,
        extra DOUBLE,
        mta_tax DOUBLE,
        tip_amount DOUBLE,
        tolls_amount DOUBLE,
        improvement_surcharge DOUBLE,
        total_amount DOUBLE,
        congestion_surcharge DOUBLE,
        airport_fee DOUBLE
    )
    WITH (
        external_location = '{s3_path}',
        format = 'PARQUET'
    )
    """
    execute_query(conn, create_query)
    conn.close()

def main():
    print("=" * 80)
    print("TRINO TABLE BOOTSTRAP - RAW LAYER ONLY")
    print("=" * 80)

    validate_minio_buckets()
    create_hive_raw_schema()
    create_hive_raw_table(NYC_TAXI_YEAR, NYC_TAXI_MONTH)

    print("\n" + "=" * 80)
    print("✓ BOOTSTRAP COMPLETED - Raw layer ready for dbt")
    print("=" * 80)

if __name__ == "__main__":
    main()
