SELECT
    p.snap, p.runid,
    AVG(p.x) AS cx,
    AVG(p.y) AS cy,
    AVG(p.z) AS cz,
    COUNT(*) * MAX(m.mp1) AS mtot
FROM {{ref('apply_scaling_dark')}} p
JOIN {{ref('find_mass_table')}} m
ON m.runid = p.runid
GROUP BY p.snap, p.runid