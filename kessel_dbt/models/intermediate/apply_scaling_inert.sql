SELECT
    pt.snap AS snap, pt.runid as runid,
    pt.ptype as ptype,
    pt.x * gfp.x AS x,
    pt.y * gfp.y AS y,
    pt.z * gfp.z AS z,
    pt.vx * gfp.vx AS vx,
    pt.vy * gfp.vy AS vy,
    pt.vz * gfp.vz AS vz
FROM {{ref('ingest_inert')}} pt
JOIN {{ref('pivot_conv_fac_inert')}} gfp
ON pt.snap = gfp.snap AND pt.runid = gfp.runid