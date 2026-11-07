WITH vars AS (
    SELECT
        LOG10( {{ var('halo_rad') }} / {{ var('densprof_rmin') }} ) AS diff_lograd,
        LOG10( {{ var('densprof_rmin') }} ) AS min_logrmin,
        {{var('n_dens_bins')}} AS nbins
)
SELECT
    runid, snap, effptype, bin,
    v.min_logrmin + ((bin + 1) / v.nbins) * v.diff_lograd AS log_radius,
    LOG10(cummass) - 3.0*log_radius - 0.622 AS log_density        -- where the last constant is log10 of 3/4pi.
FROM {{ ref('find_logcummass_all') }} CROSS JOIN vars v