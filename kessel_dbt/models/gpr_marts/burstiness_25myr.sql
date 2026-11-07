{% set n = ((25.0 / var('sfr_timebin_myr')) | round | int) %}

WITH moving_avgs AS (
    SELECT
        runid, bin,
        AVG(value) OVER (
            PARTITION BY runid
            ORDER BY bin
            ROWS BETWEEN {{n - 1}} PRECEDING AND CURRENT ROW
        ) AS sfr_avged
    FROM {{ ref('star_formation_rate') }}
)
SELECT
    runid,
    STDDEV_POP(sfr_avged) / NULLIF( AVG(sfr_avged), 0 ) AS burstiness
FROM moving_avgs
GROUP BY runid
