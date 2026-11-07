SELECT
    p.snap AS snap, p.runid as runid, p.ptype as ptype,
    p.x - c.ctotx AS x,
    p.y - c.ctoty AS y,
    p.z - c.ctotz AS z,
    p.vx - c.ctotvx AS vx,
    p.vy - c.ctotvy AS vy,
    p.vz - c.ctotvz AS vz
FROM {{ref('apply_scaling_inert')}} p
JOIN {{ref('find_center_iso')}} c
ON p.snap = c.snap AND p.runid = c.runid