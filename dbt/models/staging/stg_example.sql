/*
Modelo Staging Template - CUSTOMIZE AQUI

TODO:
1. Renomeie para: stg_<sua_tabela>.sql
2. Configure source em staging/sources.yml
3. Adicione transformações básicas
4. Documente em staging/schema.yml

Exemplo completo em: examples/dbt_models/stg_nyc_taxi_trips.sql
*/

WITH source AS (
    -- TODO: Configure sua source em sources.yml
    SELECT * FROM {{ source('raw', 'your_table') }}
),

cleaned AS (
    SELECT
        -- TODO: Adicione suas colunas aqui
        id,
        name,
        created_at,
        value
    FROM source
    WHERE id IS NOT NULL  -- TODO: Adicione filtros
)

SELECT * FROM cleaned
