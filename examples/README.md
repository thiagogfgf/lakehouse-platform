# 📚 Exemplos de Referência

Pipeline completa funcional usando dados **NYC Yellow Taxi** como exemplo.

Use estes arquivos como **referência** ao implementar sua própria pipeline.

---

## 📁 Conteúdo

### `scripts/`
- **`ingest_nyc_taxi.py`**: Ingestão de dados da API NYC Open Data
  - Download de Parquet
  - Upload para MinIO
  - Particionamento por ano/mês

- **`bootstrap_tables_nyc_taxi.py`**: Criação de schemas e tabelas
  - Schema raw (Hive external table)
  - Schema e tabelas com tipos específicos
  - Particionamento temporal

### `dags/`
- **`nyc_taxi_pipeline.py`**: DAG Airflow completa
  - 6 tasks sequenciais
  - Ingestão → Bootstrap → dbt → Tests
  - Configuração de retries
  - Tags e descrição

### `dbt_models/`
- **`stg_nyc_taxi_trips.sql`**: Modelo staging
  - Limpeza de dados
  - Renomeação de colunas
  - Cálculo de trip_id (MD5)
  - Filtros de qualidade

- **`int_trips_enriched.sql`**: Modelo intermediate
  - Categorização de distâncias
  - Cálculo de métricas
  - Lógica de negócio

- **`fct_trips.sql`**: Tabela de fatos
  - Modelo final otimizado
  - Join com dimensões
  - Métricas calculadas

- **`dim_dates.sql`**: Dimensão de datas
  - Calendário completo
  - Hierarquias temporais

- **`dim_locations.sql`**: Dimensão de locais
  - Zonas de pickup/dropoff

- **`sources.yml`**: Configuração de sources
  - Documentação completa
  - Testes de qualidade

---

## 🚀 Como Rodar o Exemplo

### 1. Copiar arquivos de exemplo

```bash
# Copiar scripts
cp examples/scripts/ingest_nyc_taxi.py scripts/
cp examples/scripts/bootstrap_tables_nyc_taxi.py scripts/bootstrap_tables.py

# Copiar DAG
cp examples/dags/nyc_taxi_pipeline.py airflow/dags/

# Copiar modelos dbt
cp examples/dbt_models/*.sql dbt/models/staging/
cp examples/dbt_models/*.sql dbt/models/marts/
cp examples/dbt_models/sources.yml dbt/models/staging/
```

### 2. Subir ambiente

```bash
docker compose up -d
```

### 3. Executar pipeline

```bash
docker exec airflow-webserver airflow dags trigger nyc_taxi_pipeline
```

### 4. Verificar dados

```bash
docker exec -it trino-coordinator trino --catalog iceberg --schema marts

trino:marts> SELECT COUNT(*) FROM fct_trips;
# Resultado: ~150k registros
```

---

## 📊 Dataset

**NYC Yellow Taxi Trip Records**
- Fonte: NYC Open Data (https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- Período: Janeiro 2023
- Registros: ~153k viagens
- Formato: Parquet

**Campos principais:**
- `VendorID`: ID do vendor
- `tpep_pickup_datetime`: Data/hora de pickup
- `tpep_dropoff_datetime`: Data/hora de dropoff
- `passenger_count`: Número de passageiros
- `trip_distance`: Distância da viagem
- `fare_amount`: Valor da tarifa
- `tip_amount`: Gorjeta
- `total_amount`: Valor total

---

## 🎯 O que Aprender com Este Exemplo

### Ingestão (`ingest_nyc_taxi.py`)
- ✅ Download de API externa
- ✅ Conversão Parquet → S3
- ✅ Particionamento temporal
- ✅ Error handling

### Bootstrap (`bootstrap_tables_nyc_taxi.py`)
- ✅ Criação de schemas
- ✅ Tabelas Hive external
- ✅ Definição de tipos Trino
- ✅ Localização S3

### DAG Airflow (`nyc_taxi_pipeline.py`)
- ✅ Dependências entre tasks
- ✅ Python operators
- ✅ Bash operators
- ✅ Retry logic
- ✅ Schedule configuration

### dbt Models
- ✅ **Staging**: Limpeza e padronização
- ✅ **Intermediate**: Transformações complexas
- ✅ **Marts**: Modelos analíticos
- ✅ **Testes**: Qualidade de dados
- ✅ **Documentação**: Schema.yml completo

---

## 🔄 Adaptando para Seus Dados

Para cada arquivo de exemplo, identifique:

1. **Variáveis específicas**: `NYC_TAXI_YEAR`, `NYC_TAXI_MONTH`
2. **Schemas de dados**: Colunas e tipos
3. **Lógica de negócio**: Cálculos específicos
4. **Nomenclatura**: Nomes de tabelas e campos

Substitua pelos seus equivalentes!

---

## 💡 Dicas

- Compare o exemplo com os templates em `templates/`
- Use o exemplo como guia, não copie direto
- Adapte a lógica de negócio para seu caso
- Mantenha a estrutura de pastas e naming conventions

---

Voltar para: [README principal](../README.md)
