WITH pdf AS (
    SELECT
        snap, runid, effptype,
        CAST(
            LEAST(
                FLOOR( p.r3d / {{var('halo_rad')}} * {{var('n_dens_bins')}} ), 
                {{var('n_dens_bins')}} - 1 
            )
        AS INT) AS bin,
        SUM(p.m) AS val
    FROM {{ ref('collect_r3d_all_ptypes') }} p
    WHERE p.r3d BETWEEN 0 AND {{var('halo_rad')}}
    GROUP BY effptype, bin, snap, runid
)
SELECT
    runid, snap, effptype, bin, val,
    SUM(val) OVER (
        PARTITION BY snap, runid, effptype
        ORDER BY bin        
    ) AS cummass
FROM pdf
