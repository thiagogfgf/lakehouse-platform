# 🏗️ Arquitetura Completa - Distributed Lakehouse

## 📦 COMPONENTES (Containers Docker)

### Camada de Storage
```
┌─────────────────────────────────────────┐
│  MinIO (Object Storage - S3-like)       │
│  Porta: 9000 (API), 9001 (Console)      │
│                                         │
│  Buckets:                               │
│  ├─ raw/                                │
│  │   └─ nyc_taxi/yellow/               │
│  │       └─ year=2023/month=01/        │
│  │           └─ *.parquet (153K rows)  │
│  │                                     │
│  └─ warehouse/hive/                     │
│      ├─ staging.db/                    │
│      ├─ intermediate.db/               │
│      └─ marts.db/                      │
│          ├─ fct_trips/                 │
│          │   ├─ data/*.parquet         │
│          │   └─ metadata/*.json        │
│          ├─ dim_dates/                 │
│          └─ dim_locations/             │
└─────────────────────────────────────────┘
```

### Camada de Metadados
```
┌─────────────────────────────────────────┐
│  Hive Metastore (Metadata Catalog)      │
│  Porta: 9083 (Thrift)                   │
│                                         │
│  Backend: PostgreSQL                    │
│  Database: metastore                    │
│                                         │
│  Armazena:                              │
│  - Schemas (raw, staging, marts)        │
│  - Tabelas (nyc_taxi_trips, fct_trips) │
│  - Colunas e tipos                      │
│  - Localizações S3 (s3a://...)         │
│  - Tipo de tabela (Hive ou Iceberg)    │
└─────────────────────────────────────────┘
```

### Camada de Query Engine
```
┌─────────────────────────────────────────┐
│  Trino Coordinator                      │
│  Porta: 8080 (UI + JDBC)                │
│                                         │
│  Catálogos configurados:                │
│  ├─ hive                                │
│  │   └─ Para tabelas Hive (raw)        │
│  └─ iceberg                             │
│      └─ Para tabelas Iceberg (marts)   │
└─────────────────────────────────────────┘
         │
         ├── Workers (escalam horizontalmente)
         │
┌────────┴────────────────────────────────┐
│  Trino Worker (1..N)                    │
│  Processa queries em paralelo           │
└─────────────────────────────────────────┘
```

### Camada de Transformação
```
┌─────────────────────────────────────────┐
│  dbt (Data Build Tool)                  │
│  Rodando dentro do Airflow              │
│                                         │
│  Modelos:                               │
│  ├─ staging/                            │
│  │   └─ stg_nyc_taxi_trips.sql         │
│  ├─ intermediate/                       │
│  │   └─ int_trips_enriched.sql         │
│  └─ marts/                              │
│      ├─ fct_trips.sql                   │
│      ├─ dim_dates.sql                   │
│      └─ dim_locations.sql               │
└─────────────────────────────────────────┘
```

### Camada de Orquestração
```
┌─────────────────────────────────────────┐
│  Apache Airflow                         │
│  Porta: 8081 (Web UI)                   │
│                                         │
│  DAG: nyc_taxi_pipeline                 │
│  ├─ validate_buckets                    │
│  ├─ ingest_nyc_taxi                     │
│  ├─ create_hive_raw_schema              │
│  ├─ create_hive_raw_table               │
│  ├─ dbt_run                             │
│  └─ dbt_test                            │
└─────────────────────────────────────────┘
```

---

## 🔄 FLUXO DE DADOS (Data Flow)

### 1️⃣ INGESTÃO (Airflow Task: ingest_nyc_taxi)
```
NYC Open Data API
      │
      │ Download Parquet
      ▼
scripts/ingest_nyc_taxi.py
      │
      │ Upload via S3 API
      ▼
MinIO: s3://raw/nyc_taxi/yellow/year=2023/month=01/
      │
      │ Parquet files (153,338 rows)
      ▼
[RAW LAYER - Dados originais imutáveis]
```

### 2️⃣ REGISTRO DE METADATA (Airflow Task: create_hive_raw_table)
```
scripts/bootstrap_tables.py
      │
      │ CREATE TABLE via Trino
      ▼
Trino → Hive Metastore
      │
      │ Registra:
      │ - Schema: raw
      │ - Table: nyc_taxi_trips
      │ - Location: s3a://raw/...
      │ - Format: PARQUET
      │ - Type: HIVE
      ▼
[Tabela disponível para queries]
```

### 3️⃣ TRANSFORMAÇÃO (Airflow Task: dbt_run)
```
dbt run
      │
      │ Lê source: hive.raw.nyc_taxi_trips
      ▼
models/staging/stg_nyc_taxi_trips.sql
      │ - Renomeia colunas
      │ - Limpeza básica (nulls, valores inválidos)
      │ - Cria trip_id (MD5)
      ▼
[VIEW no schema staging]
      │
      ▼
models/intermediate/int_trips_enriched.sql
      │ - Adiciona categorias
      │ - Calcula métricas
      ▼
[VIEW no schema intermediate]
      │
      ▼
models/marts/fct_trips.sql
      │ - Modelo final
      │ - Otimizado para BI
      ▼
Trino executa: CREATE TABLE iceberg.marts.fct_trips
      │
      │ Escreve no MinIO
      ▼
s3a://warehouse/hive/marts.db/fct_trips/
      ├─ data/*.parquet (149,848 rows)
      └─ metadata/*.json (Iceberg metadata)
      │
      │ Registra no Metastore
      ▼
Hive Metastore
      └─ table_type = 'ICEBERG'
```

### 4️⃣ VALIDAÇÃO (Airflow Task: dbt_test)
```
dbt test
      │
      ▼
tests/marts/assert_positive_fare.sql
      │ - Verifica qualidade dos dados
      │ - Falha se > 5% com problemas
      ▼
[Pipeline completo validado ✓]
```

---

## 🎯 ARQUITETURA DE CATÁLOGOS

### Como os 2 catálogos funcionam:

```
┌─────────────────────────────────────────────────────┐
│                  TRINO COORDINATOR                   │
└──────────────────┬──────────────────┬───────────────┘
                   │                  │
         ┌─────────┴─────┐   ┌────────┴────────┐
         │ HIVE CATALOG  │   │ ICEBERG CATALOG │
         │ (connector)   │   │   (connector)   │
         └───────┬───────┘   └────────┬────────┘
                 │                    │
                 └──────────┬─────────┘
                            │
                            │ Ambos consultam
                            │ o mesmo metastore
                            ▼
         ┌──────────────────────────────────┐
         │    HIVE METASTORE (PostgreSQL)   │
         │                                  │
         │  Schemas:                        │
         │  ├─ raw                          │
         │  ├─ staging                      │
         │  ├─ intermediate                 │
         │  └─ marts                        │
         │                                  │
         │  Tabelas:                        │
         │  ├─ nyc_taxi_trips (Hive)        │
         │  ├─ stg_nyc_taxi_trips (View)    │
         │  └─ fct_trips (Iceberg)          │
         └──────────────────────────────────┘
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
         ┌───────────────┐   ┌─────────────────┐
         │  HIVE TABLE   │   │  ICEBERG TABLE  │
         ├───────────────┤   ├─────────────────┤
         │ Parquet       │   │ Parquet + Meta  │
         │ Simples       │   │ ACID            │
         │ Imutável      │   │ Time Travel     │
         │ Raw Layer     │   │ Marts Layer     │
         └───────────────┘   └─────────────────┘
```

### Regra de uso:

```
hive.raw.*           → Acessa tabelas Hive (raw data)
iceberg.staging.*    → Acessa views dbt (staging)
iceberg.intermediate.* → Acessa views dbt (intermediate)
iceberg.marts.*      → Acessa tabelas Iceberg (marts)
```

⚠️ **IMPORTANTE**:
- `iceberg.raw.*` NÃO USE! (Mostra tabela, mas dá erro)
- `hive.marts.*` EVITE! (Funciona, mas perde features Iceberg)

---

## 📊 CAMADAS DO LAKEHOUSE (Medallion Architecture)

```
┌────────────────────────────────────────────────────┐
│  RAW LAYER (Bronze)                                │
├────────────────────────────────────────────────────┤
│  Formato:  Hive External Table (Parquet)           │
│  Catalog:  hive                                    │
│  Schema:   raw                                     │
│  Tabela:   nyc_taxi_trips                          │
│  Rows:     153,338                                 │
│  Local:    s3a://raw/nyc_taxi/yellow/...          │
│  Imutável: ✓ (append-only)                        │
└────────────────────────────────────────────────────┘
                      │
                      │ dbt lê via source()
                      ▼
┌────────────────────────────────────────────────────┐
│  STAGING LAYER (Silver)                            │
├────────────────────────────────────────────────────┤
│  Formato:  View (não persiste dados)               │
│  Catalog:  iceberg                                 │
│  Schema:   staging                                 │
│  Tabela:   stg_nyc_taxi_trips                      │
│  Função:   Limpeza, renomear, tipos                │
└────────────────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────┐
│  INTERMEDIATE LAYER                                │
├────────────────────────────────────────────────────┤
│  Formato:  View (não persiste dados)               │
│  Catalog:  iceberg                                 │
│  Schema:   intermediate                            │
│  Tabela:   int_trips_enriched                      │
│  Função:   Joins, agregações, lógica de negócio   │
└────────────────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────┐
│  MARTS LAYER (Gold)                                │
├────────────────────────────────────────────────────┤
│  Formato:  Iceberg Table (Parquet + metadata)      │
│  Catalog:  iceberg                                 │
│  Schema:   marts                                   │
│  Tabelas:  fct_trips (149,848 rows)               │
│            dim_dates                               │
│            dim_locations                           │
│  Local:    s3a://warehouse/hive/marts.db/...      │
│  Features: ACID, Time Travel, Schema Evolution     │
└────────────────────────────────────────────────────┘
```

---

## 🔌 PONTOS DE ACESSO (Como consumir os dados)

### 1. DBeaver / DataGrip (SQL Client)
```
Host:     localhost
Port:     8080
Catalog:  iceberg (ou hive)
Schema:   marts
User:     admin
Driver:   Trino JDBC
```

### 2. Trino CLI
```bash
docker exec -it trino-coordinator trino \
  --catalog iceberg \
  --schema marts
```

### 3. Python (trino-python-client)
```python
import trino
conn = trino.dbapi.connect(
    host='localhost',
    port=8080,
    user='admin',
    catalog='iceberg',
    schema='marts'
)
```

### 4. dbt docs (Documentação)
```
http://localhost:8083
```

### 5. Airflow UI (Pipeline)
```
http://localhost:8081
```

### 6. Trino UI (Query Monitor)
```
http://localhost:8080
```

### 7. MinIO Console (Storage)
```
http://localhost:9001
User: minioadmin
Pass: minioadmin
```

---

## 📈 ESTATÍSTICAS DO SISTEMA

### Dados:
- **Raw**: 153,338 registros (NYC Taxi Jan 2023)
- **Marts**: 149,848 registros (97.7% após limpeza)
- **Pass rate**: 3,490 registros rejeitados (2.3%)

### Qualidade:
- ✅ 0 nulls em colunas críticas
- ✅ Fare médio: $18.54
- ✅ Distância média: 3.42 miles
- ✅ Todos os testes dbt passando

### Performance:
- Pipeline completo: ~20 segundos
- dbt run: ~8 segundos
- dbt test: ~4 segundos

---

## 🎨 SUGESTÕES PARA O DESENHO EXCALIDRAW

### Cores sugeridas:
- **MinIO**: Laranja (#FF6B6B)
- **Hive Metastore**: Amarelo (#FFD93D)
- **Trino**: Azul (#4ECDC4)
- **Airflow**: Verde (#95E1D3)
- **dbt**: Roxo (#A8DADC)

### Componentes principais:
1. Caixas para cada container
2. Setas mostrando fluxo de dados
3. Ícones de banco de dados para storage
4. Números nos passos (1→2→3→4)
5. Legendas para cada camada (Raw/Staging/Marts)

### Seções do diagrama:
1. **Topo**: Camada de consumo (DBeaver, Python)
2. **Centro**: Processing (Trino, dbt)
3. **Meio**: Metadados (Hive Metastore)
4. **Base**: Storage (MinIO)
5. **Lateral**: Orquestração (Airflow)

---

## 🚀 COMANDOS ÚTEIS

### Ver catálogos:
```sql
SHOW CATALOGS;
```

### Ver schemas:
```sql
SHOW SCHEMAS IN iceberg;
```

### Ver tabelas:
```sql
SHOW TABLES IN iceberg.marts;
```

### Query exemplo:
```sql
SELECT
    pickup_date_key,
    COUNT(*) as trips,
    AVG(fare_amount) as avg_fare
FROM iceberg.marts.fct_trips
GROUP BY pickup_date_key
ORDER BY pickup_date_key DESC
LIMIT 10;
```

### Ver snapshots Iceberg:
```sql
SELECT * FROM iceberg.marts."fct_trips$snapshots";
```

### Rerun pipeline:
```bash
docker exec airflow-webserver airflow dags trigger nyc_taxi_pipeline
```

---

Bora fazer esse desenho! 🎨
