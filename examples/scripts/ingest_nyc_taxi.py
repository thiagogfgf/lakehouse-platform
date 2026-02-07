#!/usr/bin/env python3
"""NYC Taxi Data Ingestion Script"""

import os
import sys
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq
import boto3
from botocore.client import Config
import requests
import tempfile

# Config
YEAR = os.getenv("NYC_TAXI_YEAR", "2023")
MONTH = os.getenv("NYC_TAXI_MONTH", "01").zfill(2)
COLOR = os.getenv("NYC_TAXI_COLOR", "yellow")
SAMPLE_FRACTION = float(os.getenv("NYC_TAXI_SAMPLE_FRACTION", "0.05"))
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin123")

NYC_TAXI_BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
BUCKET_NAME = "raw"
S3_PATH = f"nyc_taxi/{COLOR}/year={YEAR}/month={MONTH}"

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

def download_parquet(year, month, color):
    filename = f"{color}_tripdata_{year}-{month}.parquet"
    url = f"{NYC_TAXI_BASE_URL}/{filename}"
    print(f"Downloading: {url}")
    
    response = requests.get(url, stream=True, timeout=300)
    response.raise_for_status()
    
    temp_file = Path(tempfile.gettempdir()) / filename
    with open(temp_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"✓ Downloaded: {temp_file}")
    return temp_file

def sample_parquet(input_path, sample_fraction):
    if sample_fraction >= 1.0:
        return input_path
    
    print(f"Sampling {sample_fraction*100:.1f}%...")
    df = pd.read_parquet(input_path)
    df_sampled = df.sample(frac=sample_fraction, random_state=42)
    
    output_path = input_path.with_suffix(".sampled.parquet")
    df_sampled.to_parquet(output_path, index=False, compression="snappy")
    print(f"✓ Sampled: {len(df):,} → {len(df_sampled):,} rows")
    return output_path

def upload_to_minio(local_path, s3_key):
    print(f"Uploading to s3://{BUCKET_NAME}/{s3_key}")
    s3_client = get_s3_client()
    s3_client.upload_file(str(local_path), BUCKET_NAME, s3_key)
    print("✓ Uploaded successfully")

def main():
    print("=" * 80)
    print("NYC TAXI DATA INGESTION")
    print("=" * 80)
    
    downloaded_file = download_parquet(YEAR, MONTH, COLOR)
    final_file = sample_parquet(downloaded_file, SAMPLE_FRACTION)
    
    s3_key = f"{S3_PATH}/{final_file.name}"
    upload_to_minio(final_file, s3_key)
    
    # Cleanup
    if downloaded_file.exists():
        downloaded_file.unlink()
    if final_file != downloaded_file and final_file.exists():
        final_file.unlink()
    
    print("=" * 80)
    print("✓ INGESTION COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    main()
