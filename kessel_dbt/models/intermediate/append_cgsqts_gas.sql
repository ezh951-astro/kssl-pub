WITH combined AS (
    SELECT 
        attrmeta.name AS name,
        attrmeta.snap AS snap, attrmeta.runid AS runid,
        attrmeta.to_cgs * cosmo.cosmo_fac AS factor
    FROM {{ref('ingest_attribute_meta')}} attrmeta
    JOIN {{ref('find_cosmo_fac')}} cosmo
    ON cosmo.name = attrmeta.name AND cosmo.ptype = attrmeta.ptype
    AND cosmo.snap = attrmeta.snap AND cosmo.runid = attrmeta.runid
    WHERE attrmeta.ptype = 0
),
pivoted_factors AS (
    SELECT
    snap, runid,
    MAX(CASE WHEN name = 'U' THEN factor END) AS fac_U,
    MAX(CASE WHEN name = 'rho' THEN factor END) AS fac_rho
    FROM combined
    GROUP BY snap, runid
)
SELECT p.*,
    p.U * f.fac_U AS U_cgs,
    p.rho * f.fac_rho AS rho_cgs
FROM {{ref('ingest_gas')}} p 
JOIN pivoted_factors f
ON p.snap = f.snap AND p.runid = f.runid