WITH final_snap_by_run AS (
    SELECT
        runid,
        MAX(snap) AS last_snap_of_run
    FROM {{ref('stellar_mass_total')}}
    GROUP BY runid
),
final_snap_all AS (
    SELECT
        MIN(last_snap_of_run) AS final_snap_of_set
    FROM final_snap_by_run
)
SELECT
    runid, LOG10(m.mstartot) AS logmstar
FROM {{ref('stellar_mass_total')}} m
CROSS JOIN final_snap_all fs
WHERE m.snap = fs.final_snap_of_set