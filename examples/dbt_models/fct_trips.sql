WITH enriched_trips AS (
    SELECT * FROM {{ ref('int_trips_enriched') }}
),

pickup_dates AS (
    SELECT date_key, full_date
    FROM {{ ref('dim_dates') }}
)

SELECT
    t.trip_id,
    pd.date_key as pickup_date_key,
    t.pickup_location_id,
    t.dropoff_location_id,
    t.vendor_id,
    t.payment_type,
    t.payment_type_desc,
    t.pickup_datetime as tpep_pickup_datetime,
    t.dropoff_datetime as tpep_dropoff_datetime,
    t.trip_distance,
    t.trip_duration_minutes,
    t.passenger_count,
    t.fare_amount,
    t.tip_amount,
    t.total_amount,
    t.tip_percentage,
    t.avg_speed_mph,
    t.trip_distance_category
FROM enriched_trips t
LEFT JOIN pickup_dates pd ON t.pickup_date = pd.full_date
