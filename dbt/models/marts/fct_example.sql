/*
Modelo Marts Template - CUSTOMIZE AQUI

TODO:
1. Renomeie para: fct_<sua_metrica>.sql ou dim_<sua_dimensao>.sql
2. Referencie modelos staging com {{ ref() }}
3. Adicione agregações/joins
4. Configure materialização (table/incremental)
5. Documente em marts/schema.yml

Exemplo completo em: examples/dbt_models/fct_trips.sql
*/

{{ config(
    materialized='table'
) }}

WITH staging AS (
    SELECT * FROM {{ ref('stg_example') }}
),

aggregated AS (
    SELECT
        -- TODO: Adicione suas métricas/dimensões aqui
        DATE(created_at) as date_key,
        COUNT(*) as total_records,
        SUM(value) as total_value,
        AVG(value) as avg_value
    FROM staging
    GROUP BY DATE(created_at)
)

SELECT * FROM aggregated
