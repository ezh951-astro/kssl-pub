SELECT
    p.snap AS snap, p.runid as runid,
    p.x - c.ctotx AS x,
    p.y - c.ctoty AS y,
    p.z - c.ctotz AS z
FROM {{ref('apply_scaling_dark')}} p
JOIN {{ref('find_center_iso')}} c
ON p.snap = c.snap AND p.runid = c.runid