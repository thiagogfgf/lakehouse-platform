WITH source AS (
    SELECT * FROM {{ source('raw', 'nyc_taxi_trips') }}
),

cleaned AS (
    SELECT
        VendorID as vendor_id,
        PULocationID as pickup_location_id,
        DOLocationID as dropoff_location_id,
        tpep_pickup_datetime as pickup_datetime,
        tpep_dropoff_datetime as dropoff_datetime,
        COALESCE(passenger_count, 1.0) as passenger_count,
        trip_distance,
        payment_type,
        fare_amount,
        tip_amount,
        total_amount,
        DATE(tpep_pickup_datetime) as pickup_date,
        CAST(
            DATE_DIFF('second', tpep_pickup_datetime, tpep_dropoff_datetime) / 60.0 AS DOUBLE
        ) as trip_duration_minutes
    FROM source
    WHERE tpep_pickup_datetime IS NOT NULL
        AND tpep_dropoff_datetime IS NOT NULL
        AND trip_distance > 0
        AND fare_amount >= 0
        AND total_amount >= 0
)

SELECT
    MD5(to_utf8(CAST(vendor_id AS VARCHAR) || CAST(pickup_datetime AS VARCHAR))) as trip_id,
    *
FROM cleaned
