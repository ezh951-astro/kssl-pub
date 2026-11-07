SELECT
    runid, snap, effptype, bin,
    (bin + 1) / {{var('n_dens_bins')}} * {{var('halo_rad')}} AS radius,
    SQRT( u.grav * cummass / radius ) AS velocity
FROM {{ ref('find_lincummass_all') }}
CROSS JOIN {{ ref('find_physical_constants') }} u