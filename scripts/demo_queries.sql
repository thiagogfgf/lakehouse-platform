-- Demo Queries
SET SESSION query_max_run_time = '10m';

SELECT COUNT(*) as total_trips FROM iceberg.marts.fct_trips;

SELECT 
    pickup_location_id,
    COUNT(*) as trip_count,
    AVG(fare_amount) as avg_fare
FROM iceberg.marts.fct_trips
GROUP BY pickup_location_id
ORDER BY trip_count DESC
LIMIT 20;

SELECT 
    payment_type_desc,
    COUNT(*) as count,
    AVG(tip_percentage) as avg_tip_pct
FROM iceberg.marts.fct_trips
GROUP BY payment_type_desc;
