# Como conectar o DBeaver no Lakehouse

## 1. Instalar DBeaver

Download: https://dbeaver.io/download/

## 2. Adicionar Driver Trino

1. Database → Driver Manager → New
2. Driver Name: `Trino`
3. Class Name: `io.trino.jdbc.TrinoDriver`
4. URL Template: `jdbc:trino://{host}:{port}/{database}`
5. Default Port: `8080`
6. Libraries → Add Maven Artifact:
   - Group ID: `io.trino`
   - Artifact ID: `trino-jdbc`
   - Version: `438`

Ou baixe direto:
```
https://repo1.maven.org/maven2/io/trino/trino-jdbc/438/trino-jdbc-438.jar
```

## 3. Criar Conexão

1. Database → New Database Connection
2. Selecione "Trino"
3. Configure:
   - **Host:** `localhost`
   - **Port:** `8080`
   - **Database:** `iceberg` (ou `hive`)
   - **Schema:** `marts`
   - **Username:** `admin`
   - **Password:** (deixe em branco)

4. Test Connection
5. Finish

## 4. Queries de Exemplo

```sql
-- Ver todas as tabelas
SHOW TABLES IN iceberg.marts;

-- Consultar dados
SELECT
    pickup_date_key,
    COUNT(*) as trips,
    AVG(fare_amount) as avg_fare,
    AVG(trip_distance) as avg_distance
FROM iceberg.marts.fct_trips
GROUP BY pickup_date_key
ORDER BY pickup_date_key DESC
LIMIT 10;

-- Ver lineage (de onde vem os dados)
SELECT * FROM iceberg.marts.fct_trips LIMIT 100;
```

## 5. Dicas

- Use `Ctrl+Enter` para executar a query
- Use `Ctrl+Shift+E` para explicar o plano de execução
- Salve queries frequentes como Bookmarks
- Use autocomplete com `Ctrl+Space`
