-- This test allows a small number of records with negative/zero fares
-- (refunds, cancellations, adjustments are normal in real data)
-- Fails only if more than 5% of trips have this issue

WITH problematic_records AS (
    SELECT COUNT(*) as problem_count
    FROM {{ ref('fct_trips') }}
    WHERE fare_amount <= 0 OR total_amount <= 0
),
total_records AS (
    SELECT COUNT(*) as total_count
    FROM {{ ref('fct_trips') }}
)

SELECT
    p.problem_count,
    t.total_count,
    (p.problem_count * 100.0 / t.total_count) as problem_percentage
FROM problematic_records p, total_records t
WHERE (p.problem_count * 100.0 / t.total_count) > 5.0
