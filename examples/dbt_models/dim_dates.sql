WITH date_spine AS (
    SELECT DISTINCT pickup_date as date_value
    FROM {{ ref('stg_nyc_taxi_trips') }}
),

dates AS (
    SELECT
        CAST(
            YEAR(date_value) * 10000 + 
            MONTH(date_value) * 100 + 
            DAY(date_value) AS INTEGER
        ) as date_key,
        date_value as full_date,
        YEAR(date_value) as year,
        MONTH(date_value) as month,
        DAY(date_value) as day,
        DAY_OF_WEEK(date_value) as day_of_week_num,
        CASE WHEN DAY_OF_WEEK(date_value) IN (6, 7) THEN 1 ELSE 0 END as is_weekend
    FROM date_spine
)

SELECT * FROM dates
