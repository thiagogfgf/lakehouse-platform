-- ============================================
-- Diferença entre HIVE e ICEBERG Catalogs
-- ============================================

-- 1. Ver schemas em cada catálogo
SHOW SCHEMAS IN hive;
-- Resultado: raw, staging, intermediate, marts

SHOW SCHEMAS IN iceberg;
-- Resultado: raw, staging, intermediate, marts

-- 2. Ver tabelas RAW (mesma tabela, catalogs diferentes)
SHOW TABLES IN hive.raw;
-- nyc_taxi_trips (Hive/Parquet)

SHOW TABLES IN iceberg.raw;
-- nyc_taxi_trips (Iceberg, se existir)

-- 3. HIVE: Tabela simples (sem features Iceberg)
SELECT COUNT(*) FROM hive.raw.nyc_taxi_trips;
-- 153,338 registros

-- Tentar ver snapshots (NÃO FUNCIONA no Hive)
-- SELECT * FROM hive.raw."nyc_taxi_trips$snapshots";
-- ❌ Error: Table not found

-- 4. ICEBERG: Tabela com features avançadas
SELECT COUNT(*) FROM iceberg.marts.fct_trips;
-- 149,848 registros

-- Ver histórico de versões (SÓ FUNCIONA no Iceberg)
SELECT
    committed_at,
    snapshot_id,
    operation
FROM iceberg.marts."fct_trips$snapshots"
ORDER BY committed_at DESC;
-- ✅ Funciona! Mostra histórico de mudanças

-- 5. Ver arquivos físicos (SÓ ICEBERG)
SELECT
    file_path,
    record_count,
    file_size_in_bytes / 1024 / 1024 as size_mb
FROM iceberg.marts."fct_trips$files"
LIMIT 5;

-- 6. Time Travel (SÓ ICEBERG)
-- Ver dados de um snapshot específico
SELECT COUNT(*)
FROM iceberg.marts.fct_trips
FOR VERSION AS OF 6817897627008667851;

-- ============================================
-- RESUMO
-- ============================================
-- HIVE catalog:   Tabelas simples (raw layer)
-- ICEBERG catalog: Tabelas avançadas (staging + marts)
-- Ambos usam o mesmo Hive Metastore para metadados
-- Mas Iceberg tem features extras (ACID, time travel)
