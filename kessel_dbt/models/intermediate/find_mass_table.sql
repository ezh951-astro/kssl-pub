{{ config(materialized='table') }}

WITH massf AS ( -- actually this shouldnt vary from snap to snap
    SELECT mass_fac FROM {{ref('unit_conversions')}} WHERE system_name='{{ var('unit_system') }}'
)
SELECT
    runid,
    MAX( CAST( h.UnitMass_in_g AS DOUBLE) * CAST( h.m_p1 AS DOUBLE)  / massf.mass_fac ) AS mp1,
    MAX( CAST( h.UnitMass_in_g AS DOUBLE) * CAST( h.m_p2 AS DOUBLE)  / massf.mass_fac ) AS mp2,
    MAX( CAST( h.UnitMass_in_g AS DOUBLE) * CAST( h.m_p3 AS DOUBLE)  / massf.mass_fac ) AS mp3,
    MAX( CAST( h.UnitMass_in_g AS DOUBLE) * CAST( h.m_p5 AS DOUBLE)  / massf.mass_fac ) AS mp5
FROM {{ref('ingest_header_meta')}} h
CROSS JOIN massf -- this shouldn't depend on snapid and runid, should add test specifying such
GROUP BY runid