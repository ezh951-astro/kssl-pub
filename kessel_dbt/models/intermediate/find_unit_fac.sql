WITH scaletable AS ( -- actually this shouldnt vary from snap to snap
    SELECT
        a.name AS name, a.ptype AS ptype,
        a.snap AS snap, a.runid AS runid,
        POWER( u.dist_fac, a.length_scaling ) as facd,
        POWER( u.mass_fac, a.mass_scaling ) as facm,
        POWER( u.vel_fac, a.velocity_scaling ) as facv,
        to_cgs
    FROM {{ref('ingest_attribute_meta')}} a
    JOIN {{ref('unit_conversions')}} u
    ON u.system_name = '{{ var('unit_system') }}'
)
SELECT
    name, ptype, snap, runid,
    to_cgs / facd / facm / facv as unit_fac
FROM scaletable