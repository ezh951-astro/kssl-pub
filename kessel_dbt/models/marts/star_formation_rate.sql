{% set tmax = var('time_max_myr') %}
{% set timebin = var('sfr_timebin_myr') %}
{% set nbins = (tmax / timebin) | round(0, 'ceil') | int %}

WITH max_snaps AS (
    SELECT
        runid,
        MAX(snap) AS maxsnap
    FROM {{ ref('cast_final_table_star') }}
    GROUP BY runid
),
final_snap AS (
    SELECT
        p.runid, p.tForm, p.m
    FROM {{ ref('cast_final_table_star') }} p
    JOIN max_snaps ms ON p.runid = ms.runid
    WHERE p.snap = ms.maxsnap
),
binned AS (
    SELECT
        runid,
        CAST(
            LEAST(FLOOR(tForm / {{ timebin }}), {{ nbins }} - 1)    -- tForm = tmax lands in the last bin
        AS INT) AS bin,
        m
    FROM final_snap
    WHERE tForm BETWEEN 0 AND {{ tmax }}
),
all_bins AS (   -- evry (runid, bin) pair, so bins without star formation show up as zero SFR
    SELECT
        ms.runid, b.bin
    FROM max_snaps ms
    CROSS JOIN range(0, {{ nbins }}) b(bin)
)
SELECT
    ab.runid,
    ab.bin,
    (ab.bin + 1) * {{ timebin }} AS t_of_bin,
    COALESCE( SUM(bn.m), 0 ) / {{ timebin }} AS value
FROM all_bins ab
LEFT JOIN binned bn
ON ab.runid = bn.runid AND ab.bin = bn.bin
GROUP BY ab.runid, ab.bin
ORDER BY ab.runid, ab.bin
