-- ============================================
-- Trino Catalog Explorer
-- ============================================
-- Execute essas queries no Trino CLI ou UI

-- 1. Ver todos os catálogos
SHOW CATALOGS;

-- 2. Ver schemas no Iceberg
SHOW SCHEMAS IN iceberg;

-- 3. Ver todas as tabelas do lakehouse
SELECT
    table_schema AS schema,
    table_name AS table,
    table_type AS type
FROM iceberg.information_schema.tables
WHERE table_schema IN ('raw', 'staging', 'intermediate', 'marts')
ORDER BY table_schema, table_name;

-- 4. Ver colunas de uma tabela específica
DESCRIBE iceberg.marts.fct_trips;

-- 5. Ver estatísticas de uma tabela
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT pickup_location_id) as unique_pickup_locations,
    COUNT(DISTINCT dropoff_location_id) as unique_dropoff_locations,
    ROUND(AVG(fare_amount), 2) as avg_fare,
    ROUND(AVG(trip_distance), 2) as avg_distance
FROM iceberg.marts.fct_trips;

-- 6. Ver snapshots do Iceberg (histórico de versões)
SELECT
    committed_at,
    snapshot_id,
    operation,
    summary
FROM iceberg.marts."fct_trips$snapshots"
ORDER BY committed_at DESC;

-- 7. Ver arquivos físicos de uma tabela Iceberg
SELECT
    file_path,
    file_format,
    record_count,
    file_size_in_bytes / 1024 / 1024 as size_mb
FROM iceberg.marts."fct_trips$files";

-- 8. Ver partições (se existirem)
SELECT
    partition,
    record_count,
    file_count
FROM iceberg.marts."fct_trips$partitions";
