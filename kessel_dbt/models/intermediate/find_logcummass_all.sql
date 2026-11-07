WITH params AS (
    SELECT
        snap, runid, effptype,
        LOG10({{ var('densprof_rmin') }}) AS logrmin,
        COALESCE(SUM(m) FILTER (WHERE r3d < {{ var('densprof_rmin') }}), 0) AS middle_mass
    FROM {{ ref('collect_r3d_all_ptypes') }}
    GROUP BY snap, runid, effptype
),
pdf AS (
    SELECT
        p.snap, p.runid, p.effptype,
        CAST(
            LEAST( 
                FLOOR( (p.logr3d - params.logrmin) / (LOG10({{var('halo_rad')}})-params.logrmin) * {{var('n_dens_bins')}}), 
                {{var('n_dens_bins')}} - 1 
            )
        AS INT) AS bin,
        SUM(p.m) AS val,
        MAX(params.middle_mass) AS middle_mass
    FROM {{ ref('collect_r3d_all_ptypes') }} p 
    JOIN params 
    ON p.snap = params.snap AND p.runid = params.runid AND p.effptype = params.effptype
    WHERE p.logr3d BETWEEN params.logrmin AND LOG10({{var('halo_rad')}})
    GROUP BY bin, p.snap, p.runid, p.effptype
)
SELECT
    runid, snap, effptype, bin, val, -- central mass assumed negligible
    SUM(val) OVER (
        PARTITION BY snap, runid, effptype
        ORDER BY bin        
    ) + middle_mass AS cummass
FROM pdf