# 🚀 Setup Your Own Pipeline

Guia para customizar este template e criar sua própria data pipeline.

---

## 📋 Checklist de Customização

### 1. Configuração Básica

- [ ] Renomear o projeto no `docker-compose.yml`
- [ ] Ajustar variáveis no `.env`
- [ ] Modificar `dbt/dbt_project.yml` (nome do projeto)

### 2. Ingestão de Dados

- [ ] Criar seu script de ingestão em `scripts/ingest_<seu_dado>.py`
- [ ] Configurar source dos dados (API, CSV, database, etc)
- [ ] Definir schema dos dados raw

### 3. Schema e Tabelas

- [ ] Modificar `scripts/bootstrap_tables.py`
  - Nome das tabelas
  - Colunas e tipos
  - Particionamento (se necessário)

### 4. Transformações dbt

- [ ] Criar modelos em `dbt/models/staging/`
- [ ] Criar modelos em `dbt/models/marts/`
- [ ] Adicionar testes em `dbt/tests/`
- [ ] Documentar em `dbt/models/schema.yml`

### 5. Pipeline Airflow

- [ ] Renomear DAG em `airflow/dags/<seu_pipeline>.py`
- [ ] Ajustar tasks conforme sua necessidade
- [ ] Configurar schedule (cron)

---

## 🔧 Passo a Passo Detalhado

### Passo 1: Clone e Setup Inicial

```bash
# Clone o template
git clone <repo> my-lakehouse
cd my-lakehouse

# Copie o .env de exemplo
cp .env.example .env

# Edite as variáveis
vim .env
```

### Passo 2: Defina Seu Projeto dbt

Edite `dbt/dbt_project.yml`:

```yaml
name: 'my_project_name'  # ← Mude aqui
version: '1.0.0'
config-version: 2

profile: 'lakehouse'

models:
  my_project_name:  # ← E aqui
    staging:
      +materialized: view
      +schema: staging
    marts:
      +materialized: table
      +schema: marts
```

### Passo 3: Crie Seu Script de Ingestão

Crie `scripts/ingest_my_data.py`:

```python
#!/usr/bin/env python3
"""Ingest data from YOUR SOURCE"""

import boto3
import pandas as pd

def main():
    # 1. Extrair dados da sua fonte
    # Exemplos:
    # - API: requests.get(...)
    # - Database: pd.read_sql(...)
    # - CSV: pd.read_csv(...)
    # - Cloud Storage: download files

    df = extract_data()

    # 2. Salvar no MinIO (S3)
    s3 = boto3.client(
        's3',
        endpoint_url='http://minio:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin'
    )

    # Salvar como Parquet
    df.to_parquet('/tmp/data.parquet', index=False)

    s3.upload_file(
        '/tmp/data.parquet',
        'raw',
        'my_data/year=2024/month=01/data.parquet'
    )

    print(f"✓ {len(df)} registros ingeridos")

def extract_data():
    """Customize esta função para seu source"""
    # Exemplo: API
    # response = requests.get('https://api.example.com/data')
    # return pd.DataFrame(response.json())

    # Exemplo: Database
    # conn = psycopg2.connect(...)
    # return pd.read_sql("SELECT * FROM source_table", conn)

    # Exemplo: CSV local
    # return pd.read_csv('data/input.csv')

    pass

if __name__ == "__main__":
    main()
```

### Passo 4: Configure Schema Raw

Edite `scripts/bootstrap_tables.py`:

```python
def create_hive_raw_table(year, month):
    """Customize para seu schema"""

    # Defina suas colunas aqui
    create_query = f"""
    CREATE TABLE hive.raw.my_table (
        id BIGINT,
        name VARCHAR,
        created_at TIMESTAMP(3),
        value DOUBLE,
        category VARCHAR
        -- Adicione suas colunas
    )
    WITH (
        external_location = 's3a://raw/my_data/year={year}/month={month}/',
        format = 'PARQUET'
    )
    """
    execute_query(conn, create_query)
```

### Passo 5: Crie Modelos dbt

#### Staging Layer

Crie `dbt/models/staging/stg_my_data.sql`:

```sql
WITH source AS (
    SELECT * FROM {{ source('raw', 'my_table') }}
),

cleaned AS (
    SELECT
        id,
        LOWER(TRIM(name)) as name,
        created_at,
        value,
        category,
        -- Adicione transformações básicas
        DATE(created_at) as created_date
    FROM source
    WHERE id IS NOT NULL
        AND created_at IS NOT NULL
)

SELECT * FROM cleaned
```

#### Marts Layer

Crie `dbt/models/marts/fct_my_metrics.sql`:

```sql
WITH staging AS (
    SELECT * FROM {{ ref('stg_my_data') }}
),

aggregated AS (
    SELECT
        created_date,
        category,
        COUNT(*) as total_records,
        SUM(value) as total_value,
        AVG(value) as avg_value
    FROM staging
    GROUP BY created_date, category
)

SELECT * FROM aggregated
```

### Passo 6: Configure Sources dbt

Edite `dbt/models/staging/sources.yml`:

```yaml
version: 2

sources:
  - name: raw
    database: hive
    schema: raw
    tables:
      - name: my_table  # ← Nome da sua tabela raw
        description: "Descrição dos dados"
        columns:
          - name: id
            description: "ID único"
            tests:
              - not_null
              - unique
          # Adicione suas colunas
```

### Passo 7: Crie Testes dbt

Crie `dbt/tests/marts/test_data_quality.sql`:

```sql
-- Testa se há registros duplicados
SELECT
    id,
    COUNT(*) as count
FROM {{ ref('fct_my_metrics') }}
GROUP BY id
HAVING COUNT(*) > 1
```

### Passo 8: Configure DAG Airflow

Edite `airflow/dags/my_pipeline.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Importe seu script de ingestão
from ingest_my_data import main as ingest_main

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='my_pipeline',
    default_args=default_args,
    description='Minha pipeline customizada',
    schedule_interval='0 2 * * *',  # ← Cron (diário às 2am)
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['my-project'],
) as dag:

    ingest = PythonOperator(
        task_id='ingest_data',
        python_callable=ingest_main,
    )

    create_tables = PythonOperator(
        task_id='create_raw_tables',
        python_callable=create_hive_raw_table,
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='python3 /opt/airflow/scripts/run_dbt.py',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='python3 /opt/airflow/scripts/run_dbt_test.py',
    )

    # Defina dependências
    ingest >> create_tables >> dbt_run >> dbt_test
```

---

## 🧪 Testando Sua Pipeline

### 1. Suba o ambiente

```bash
docker compose up -d
```

### 2. Teste ingestão manualmente

```bash
docker exec airflow-webserver python3 /opt/airflow/scripts/ingest_my_data.py
```

### 3. Crie as tabelas raw

```bash
docker exec airflow-webserver python3 /opt/airflow/scripts/bootstrap_tables.py
```

### 4. Teste dbt

```bash
docker exec airflow-webserver bash -c "cd /opt/airflow/dbt && dbt run --profiles-dir ."
docker exec airflow-webserver bash -c "cd /opt/airflow/dbt && dbt test --profiles-dir ."
```

### 5. Execute o DAG completo

```bash
docker exec airflow-webserver airflow dags trigger my_pipeline
```

---

## 📊 Exemplos de Sources Comuns

### API REST

```python
import requests

def extract_from_api():
    response = requests.get('https://api.example.com/data')
    return pd.DataFrame(response.json())
```

### PostgreSQL

```python
import psycopg2

def extract_from_postgres():
    conn = psycopg2.connect(
        host='db.example.com',
        database='mydb',
        user='user',
        password='pass'
    )
    return pd.read_sql("SELECT * FROM source_table", conn)
```

### CSV/Excel

```python
def extract_from_files():
    # CSV
    df = pd.read_csv('data/input.csv')

    # Excel
    # df = pd.read_excel('data/input.xlsx', sheet_name='Sheet1')

    return df
```

### Google Sheets

```python
import gspread

def extract_from_gsheets():
    gc = gspread.service_account(filename='credentials.json')
    sheet = gc.open('My Spreadsheet').sheet1
    return pd.DataFrame(sheet.get_all_records())
```

### S3/Cloud Storage

```python
def extract_from_s3():
    df = pd.read_parquet('s3://my-bucket/data.parquet')
    return df
```

---

## 🎨 Customização Avançada

### Adicionar novo catálogo Trino

Crie `trino/catalog/my_catalog.properties`:

```properties
connector.name=<connector_type>
# Configurações específicas
```

### Adicionar workers Trino

Edite `docker-compose.yml`:

```yaml
trino-worker-2:
  <<: *trino-worker-common
  container_name: lakehouse-trino-worker-2
```

### Configurar particionamento Iceberg

No dbt model, adicione:

```sql
{{ config(
    materialized='incremental',
    partition_by=['year', 'month'],
    file_format='parquet'
) }}
```

---

## 📝 Boas Práticas

1. **Versionamento**: Commit sua configuração no Git
2. **Secrets**: Use `.env` para credenciais (nunca commit!)
3. **Documentação**: Documente seus modelos dbt
4. **Testes**: Adicione testes de qualidade
5. **Monitoramento**: Configure alertas no Airflow
6. **Incremental**: Use `incremental` models para grandes volumes

---

## 🐛 Troubleshooting

### Erro de conexão no dbt

Verifique `dbt/profiles.yml`:
```yaml
lakehouse:
  target: dev
  outputs:
    dev:
      type: trino
      host: trino-coordinator
      port: 8080
      database: iceberg
      schema: marts
      user: admin
```

### MinIO permission denied

```bash
# Dar permissão nos buckets
docker exec minio mc anonymous set download minio/raw
docker exec minio mc anonymous set download minio/lakehouse
```

### Airflow DAG não aparece

```bash
# Verificar logs
docker compose logs airflow-scheduler

# Verificar sintaxe Python
docker exec airflow-webserver python /opt/airflow/dags/my_pipeline.py
```

---

## 🚀 Próximos Passos

- [ ] Configurar alertas (Slack, email)
- [ ] Adicionar CI/CD (GitHub Actions)
- [ ] Implementar data quality framework (Great Expectations)
- [ ] Adicionar monitoring (Prometheus + Grafana)
- [ ] Configurar backup automático
- [ ] Implementar role-based access control

---

Bora criar sua pipeline! 🎯
