SELECT * FROM {{ ref('fct_trips') }}
WHERE avg_speed_mph <= 0 OR avg_speed_mph > 100
