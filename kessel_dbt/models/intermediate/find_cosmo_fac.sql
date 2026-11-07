WITH cosmo_params AS (
    SELECT
        snap, runid,
        1.0 / (1.0 + z) as scalefac,
        h_small
    FROM {{ref('ingest_header_meta')}}
)
SELECT
    a.name AS name, a.ptype AS ptype,
    a.snap AS snap, a.runid AS runid,
    EXP( a.a_scaling * LN( c.scalefac ) + a.h_scaling * LN( c.h_small ) ) AS cosmo_fac
FROM {{ref('ingest_attribute_meta')}} a
JOIN cosmo_params c
ON c.snap = a.snap AND c.runid = a.runid