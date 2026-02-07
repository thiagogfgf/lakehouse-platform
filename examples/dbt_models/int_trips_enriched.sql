WITH trips AS (
    SELECT * FROM {{ ref('stg_nyc_taxi_trips') }}
),

enriched AS (
    SELECT
        *,
        CASE
            WHEN trip_distance <= 1 THEN 'Short'
            WHEN trip_distance <= 5 THEN 'Medium'
            ELSE 'Long'
        END as trip_distance_category,
        CASE payment_type
            WHEN 1 THEN 'Credit Card'
            WHEN 2 THEN 'Cash'
            ELSE 'Other'
        END as payment_type_desc,
        fare_amount / NULLIF(trip_distance, 0) as fare_per_mile,
        tip_amount / NULLIF(fare_amount, 0) * 100 as tip_percentage,
        trip_distance / NULLIF(trip_duration_minutes / 60.0, 0) as avg_speed_mph
    FROM trips
)

SELECT * FROM enriched
WHERE trip_duration_minutes > 0
    AND avg_speed_mph > 0
    AND avg_speed_mph < 100
