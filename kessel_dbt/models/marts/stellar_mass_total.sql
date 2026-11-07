WITH snap_only AS (
    SELECT
        p.runid, p.snap,
        SUM(p.m) AS mstartot
    FROM {{ref('cast_final_table_star')}} p
    GROUP BY runid, snap
)
SELECT
    p.runid, p.snap,
    t.cf_aTime AS simtime, t.z AS redshift,
    p.mstartot
FROM snap_only p
JOIN {{ref('ingest_header_meta')}} t 
ON t.snap = p.snap AND t.runid = p.runid