WITH pickup_locations AS (
    SELECT
        pickup_location_id as location_id,
        COUNT(*) as trip_count,
        AVG(fare_amount) as avg_fare
    FROM {{ ref('int_trips_enriched') }}
    GROUP BY pickup_location_id
),

dropoff_locations AS (
    SELECT
        dropoff_location_id as location_id,
        COUNT(*) as trip_count,
        AVG(fare_amount) as avg_fare
    FROM {{ ref('int_trips_enriched') }}
    GROUP BY dropoff_location_id
),

combined AS (
    SELECT * FROM pickup_locations
    UNION ALL
    SELECT * FROM dropoff_locations
)

SELECT
    location_id,
    SUM(trip_count) as total_trips,
    AVG(avg_fare) as avg_fare_amount
FROM combined
GROUP BY location_id
