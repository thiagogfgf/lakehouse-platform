# 🏗️ Distributed Lakehouse Template

> **Template pronto para uso** de data lakehouse moderna com Docker: Trino + Iceberg + MinIO + dbt + Airflow

Clone este repositório e customize para criar sua própria pipeline de dados em minutos! Inclui exemplo funcional com dados NYC Taxi.

**Pipeline completo**: ingestão → transformação → consumo com arquitetura medallion (Raw → Staging → Marts)

---

## 🎯 Como Usar

### **Clone e customize para sua pipeline:**

```bash
# 1. Clone o template
git clone <repo> my-lakehouse
cd my-lakehouse

# 2. Customize seus scripts
cp templates/ingest_template.py scripts/ingest_my_data.py
vim scripts/ingest_my_data.py  # Implemente extract_data()

# 3. Suba o ambiente
docker compose up -d

# 4. Teste sua ingestão
docker exec airflow-webserver python3 /opt/airflow/scripts/ingest_my_data.py
```

📘 **[Guia Completo de Customização →](SETUP_YOUR_PIPELINE.md)**

💡 **Exemplos de referência** disponíveis em `examples/` (dados NYC Taxi)

---

## 📊 Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│  Camada de Consumo (SQL Clients)                        │
│  DBeaver, Python, Jupyter                               │
└────────────────────────┬────────────────────────────────┘
                         │ (SQL Queries)
┌────────────────────────┴────────────────────────────────┐
│  Trino (Distributed Query Engine)                       │
│  ┌────────────────┐        ┌──────────────────┐        │
│  │  Hive Catalog  │        │  Iceberg Catalog │        │
│  │  (Raw Layer)   │        │  (Marts Layer)   │        │
│  └────────┬───────┘        └────────┬─────────┘        │
└───────────┼──────────────────────────┼──────────────────┘
            │                          │
            └─────────┬────────────────┘
                      │
┌─────────────────────┴─────────────────────────────────┐
│  Hive Metastore (PostgreSQL)                          │
│  Catálogo unificado de metadados                      │
└─────────────────────┬─────────────────────────────────┘
                      │
┌─────────────────────┴─────────────────────────────────┐
│  MinIO (S3-compatible Object Storage)                 │
│  ┌──────────────┐         ┌─────────────────────┐    │
│  │  raw/        │    →    │  warehouse/         │    │
│  │  153K rows   │  (dbt)  │  149K rows          │    │
│  │  Parquet     │         │  Iceberg Tables     │    │
│  └──────────────┘         └─────────────────────┘    │
└───────────────────────────────────────────────────────┘
                      │
┌─────────────────────┴─────────────────────────────────┐
│  Airflow (Orquestração)                               │
│  ingest → create tables → dbt run → dbt test          │
└───────────────────────────────────────────────────────┘
```

### Fluxo de Dados (Medallion Architecture)

```
Raw (Hive)          Staging (dbt)       Marts (Iceberg)
────────────────    ─────────────────   ──────────────────
hive.raw            iceberg.staging     iceberg.marts
├─ my_table         └─ stg_*            ├─ fct_*
│  Parquet simples     (views)          │  (tables)
│  Imutável                             ├─ dim_*
│                                          ACID + Time Travel
```

---

## 🚀 Quick Start

### Pré-requisitos

- Docker + Docker Compose
- 8GB RAM mínimo
- Portas disponíveis: 8080, 8081, 9000, 9001, 5432, 5433, 9083

### 1. Clone e configure

```bash
git clone <seu-repo> my-lakehouse
cd my-lakehouse

# Copie e ajuste variáveis
cp .env.example .env
```

### 2. Customize sua pipeline

```bash
# Veja o guia completo
cat SETUP_YOUR_PIPELINE.md

# Ou use os templates
cp templates/ingest_template.py scripts/ingest_my_data.py
```

### 3. Suba o ambiente

```bash
docker compose up -d

# Aguarde ~30 segundos
docker compose ps
```

### 4. Acesse os dados

#### Via Trino CLI

```bash
# Entrar no CLI interativo
docker exec -it trino-coordinator trino --catalog iceberg --schema marts

# Executar queries
trino:marts> SELECT COUNT(*) FROM fct_trips;
# 149848

trino:marts> SELECT
    pickup_date_key,
    COUNT(*) as trips,
    ROUND(AVG(fare_amount), 2) as avg_fare
FROM fct_trips
GROUP BY pickup_date_key
ORDER BY pickup_date_key DESC
LIMIT 5;
```

#### Via DBeaver/DataGrip

1. **Baixar o driver JDBC:**
   - Driver está em: `drivers/trino-jdbc-438.jar`
   - Ou download: https://repo1.maven.org/maven2/io/trino/trino-jdbc/438/trino-jdbc-438.jar

2. **Criar conexão:**
   ```
   Host:      localhost
   Port:      8080
   Database:  iceberg
   Schema:    marts
   Username:  admin
   Password:  (vazio)
   Driver:    Trino JDBC
   ```

3. **Executar queries:**
   ```sql
   SELECT * FROM iceberg.marts.fct_trips LIMIT 100;
   ```

Guia completo: [`docs/CONNECT_DBEAVER.md`](docs/CONNECT_DBEAVER.md)

#### Via Python

```python
import trino
import pandas as pd

conn = trino.dbapi.connect(
    host='localhost',
    port=8080,
    user='admin',
    catalog='iceberg',
    schema='marts'
)

df = pd.read_sql("SELECT * FROM fct_trips LIMIT 100", conn)
print(df.head())
```

---

## 🎯 Interfaces Web

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Airflow** | http://localhost:8081 | Orquestração e monitoramento de pipelines |
| **Trino UI** | http://localhost:8080 | Monitor de queries e cluster status |
| **MinIO Console** | http://localhost:9001 | Browser de arquivos S3 (user: minioadmin / pass: minioadmin) |
| **dbt Docs** | http://localhost:8083 | Documentação interativa dos modelos dbt |

---

## 📁 Estrutura do Projeto

```
distributed-lakehouse/
├── docker-compose.yml          # Orquestração dos containers
├── .env                        # Variáveis de ambiente
│
├── airflow/
│   ├── dags/
│   │   └── nyc_taxi_pipeline.py    # DAG principal
│   └── Dockerfile
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_nyc_taxi_trips.sql
│   │   ├── intermediate/
│   │   │   └── int_trips_enriched.sql
│   │   └── marts/
│   │       ├── fct_trips.sql
│   │       ├── dim_dates.sql
│   │       └── dim_locations.sql
│   ├── tests/
│   └── profiles.yml
│
├── scripts/
│   ├── ingest_nyc_taxi.py      # Ingestão de dados
│   ├── bootstrap_tables.py     # Criação de schemas/tabelas
│   ├── run_dbt.py              # Executor do dbt
│   └── query_example.py        # Exemplo de queries Python
│
├── trino/
│   ├── coordinator/
│   │   └── config.properties
│   ├── worker/
│   │   └── config.properties
│   └── catalog/
│       ├── hive.properties     # Catálogo para raw
│       └── iceberg.properties  # Catálogo para marts
│
├── metastore/
│   ├── Dockerfile
│   └── entrypoint.sh
│
└── docs/
    ├── ARQUITETURA_COMPLETA.md  # Detalhes técnicos completos
    ├── CONNECT_DBEAVER.md       # Guia de conexão SQL clients
    └── HIVE_VS_ICEBERG.sql      # Diferenças entre catálogos
```

---

## 🔧 Comandos Úteis

### Gerenciar containers

```bash
# Ver status
docker compose ps

# Parar tudo
docker compose down

# Limpar volumes (apaga dados)
docker compose down -v

# Ver logs
docker compose logs -f trino-coordinator
docker compose logs -f airflow-scheduler
```

### Acessar containers

```bash
# Trino CLI
docker exec -it trino-coordinator trino

# Airflow bash
docker exec -it airflow-webserver bash

# MinIO CLI
docker exec minio mc ls minio/lakehouse/ --recursive
```

### Pipeline Airflow

```bash
# Listar DAGs
docker exec airflow-webserver airflow dags list

# Trigger manual
docker exec airflow-webserver airflow dags trigger nyc_taxi_pipeline

# Ver runs
docker exec airflow-webserver airflow dags list-runs --dag-id nyc_taxi_pipeline

# Ver status das tasks
docker exec airflow-webserver airflow tasks states-for-dag-run \
  nyc_taxi_pipeline <run_id>
```

### dbt

```bash
# Rodar modelos
docker exec airflow-webserver bash -c "cd /opt/airflow/dbt && dbt run --profiles-dir ."

# Rodar testes
docker exec airflow-webserver bash -c "cd /opt/airflow/dbt && dbt test --profiles-dir ."

# Gerar documentação
docker exec airflow-webserver bash -c "cd /opt/airflow/dbt && dbt docs generate --profiles-dir ."
```

---

## 💡 Conceitos Importantes

### Por que 2 catálogos (Hive e Iceberg)?

Ambos usam o **mesmo Hive Metastore** (PostgreSQL) como backend de metadados, mas:

- **Catálogo Hive**: Para tabelas raw (Parquet simples, imutáveis)
  - `hive.raw.nyc_taxi_trips`
  - Sem ACID, sem time travel
  - Formato mais simples e compatível

- **Catálogo Iceberg**: Para tabelas marts (Iceberg tables)
  - `iceberg.marts.fct_trips`
  - ACID transactions
  - Time travel (ver versões antigas)
  - Schema evolution

**Regra de ouro:**
```sql
-- ✅ Correto
SELECT * FROM hive.raw.nyc_taxi_trips;       -- Raw data
SELECT * FROM iceberg.marts.fct_trips;       -- Marts

-- ❌ Evitar
SELECT * FROM iceberg.raw.nyc_taxi_trips;    -- Dá erro
SELECT * FROM hive.marts.fct_trips;          -- Funciona mas perde features Iceberg
```

Mais detalhes: [`docs/HIVE_VS_ICEBERG.sql`](docs/HIVE_VS_ICEBERG.sql)

### Camadas de dados (Medallion)

```
Raw      → Dados originais imutáveis (Hive external table)
Staging  → Limpeza e padronização (dbt views)
Marts    → Modelos finais otimizados para BI (Iceberg tables)
```

---

## 💡 Exemplos de Referência

O diretório `examples/` contém uma pipeline completa funcional com dados NYC Taxi:

```
examples/
├── scripts/
│   ├── ingest_nyc_taxi.py              # Ingestão de API
│   └── bootstrap_tables_nyc_taxi.py    # Schema completo
├── dags/
│   └── nyc_taxi_pipeline.py            # DAG funcional
└── dbt_models/
    ├── stg_nyc_taxi_trips.sql          # Staging
    ├── int_trips_enriched.sql          # Intermediate
    ├── fct_trips.sql                   # Facts
    ├── dim_dates.sql                   # Dimensions
    └── sources.yml                     # Sources config
```

**Use como referência** ao implementar sua própria pipeline!

---

## 🐛 Troubleshooting

### Containers não sobem

```bash
# Verificar portas em uso
netstat -tulpn | grep -E "8080|8081|9000|5432"

# Ver logs
docker compose logs
```

### Airflow DAG não aparece

```bash
# Verificar permissões
ls -la airflow/dags/

# Restart do scheduler
docker compose restart airflow-scheduler
```

### Trino connection refused

```bash
# Verificar se está healthy
docker compose ps trino-coordinator

# Aguardar 30s após startup
sleep 30 && docker exec trino-coordinator trino --execute "SELECT 1"
```

### dbt tests falhando

```bash
# Ver logs detalhados
docker exec airflow-webserver bash -c "cd /opt/airflow/dbt && dbt test --profiles-dir . --debug"
```

---

## 📚 Documentação Adicional

- **[Arquitetura Completa](docs/ARQUITETURA_COMPLETA.md)**: Detalhes técnicos, diagramas, estatísticas
- **[Conectar DBeaver](docs/CONNECT_DBEAVER.md)**: Guia passo a passo para SQL clients
- **[Hive vs Iceberg](docs/HIVE_VS_ICEBERG.sql)**: Diferenças entre catálogos com exemplos

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja [`CONTRIBUTING.md`](CONTRIBUTING.md) para guidelines.

---

## 📝 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 🙋 Suporte

Problemas ou dúvidas? Abra uma [issue](https://github.com/yourusername/distributed-lakehouse/issues).

---

**Feito com ❤️ usando Trino, Iceberg, MinIO, dbt e Airflow**
