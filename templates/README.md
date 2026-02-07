# 📝 Templates e Exemplos

Arquivos template prontos para customizar sua pipeline.

---

## 📂 Estrutura de Templates

```
templates/
├── ingest_template.py              # Template de ingestão de dados
├── dag_template.py                 # Template de DAG Airflow
├── dbt_model_template.sql          # Template de modelo dbt
└── bootstrap_tables_template.py    # Template de criação de tabelas
```

---

## 🚀 Como Usar

### 1. Copiar template para seu projeto

```bash
# Exemplo: criar script de ingestão
cp templates/ingest_template.py scripts/ingest_my_data.py

# Editar e customizar
vim scripts/ingest_my_data.py
```

### 2. Customizar conforme sua necessidade

Cada template tem comentários `# CUSTOMIZE AQUI:` indicando o que mudar.

### 3. Testar

```bash
# Testar script de ingestão
docker exec airflow-webserver python3 /opt/airflow/scripts/ingest_my_data.py
```

---

## 📄 Templates Disponíveis

### ingest_template.py

Template completo de ingestão com exemplos para:
- ✅ API REST
- ✅ PostgreSQL
- ✅ CSV/Excel
- ✅ Upload para MinIO/S3

### dag_template.py

Template de DAG Airflow com:
- ✅ Configuração de schedule
- ✅ Tasks básicas (ingest, transform, test)
- ✅ Retry logic
- ✅ Alertas

### dbt_model_template.sql

Template de modelo dbt com:
- ✅ CTEs organizadas
- ✅ Comentários de documentação
- ✅ Testes sugeridos

### bootstrap_tables_template.py

Template para criação de schemas e tabelas com:
- ✅ Tabelas Hive (raw)
- ✅ Tabelas Iceberg (marts)
- ✅ Particionamento

---

## 💡 Exemplos Reais

Veja o exemplo funcional com dados NYC Taxi:
- `scripts/ingest_nyc_taxi.py`
- `airflow/dags/nyc_taxi_pipeline.py`
- `dbt/models/staging/stg_nyc_taxi_trips.sql`

---

Voltar para: [Setup Your Pipeline](../SETUP_YOUR_PIPELINE.md)
