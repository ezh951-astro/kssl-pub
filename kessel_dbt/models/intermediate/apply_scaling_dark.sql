SELECT
    pt.snap AS snap, pt.runid as runid,
    pt.x * gfp.x AS x,
    pt.y * gfp.y AS y,
    pt.z * gfp.z AS z
FROM {{ref('ingest_dark')}} pt
JOIN {{ref('pivot_conv_fac_dark')}} gfp
ON pt.snap = gfp.snap AND pt.runid = gfp.runid