

WITH com2 AS (
    SELECT
        p.snap, p.runid,
        AVG(p.x) AS cx2,
        AVG(p.y) AS cy2,
        AVG(p.z) AS cz2,
        AVG(p.vx) AS cvx2,
        AVG(p.vy) AS cvy2,
        AVG(p.vz) AS cvz2,
        COUNT(*) * MAX(m.mp2) AS mtot2
    FROM {{ref('apply_scaling_inert')}} p
    JOIN {{ref('find_mass_table')}} m ON m.runid = p.runid
    WHERE ptype=2
    GROUP BY p.snap, p.runid
),
com3 AS (
    SELECT
        p.snap, p.runid,
        AVG(p.x) AS cx3,
        AVG(p.y) AS cy3,
        AVG(p.z) AS cz3,
        AVG(p.vx) AS cvx3,
        AVG(p.vy) AS cvy3,
        AVG(p.vz) AS cvz3,
        COUNT(*) * MAX(m.mp3) AS mtot3
    FROM {{ref('apply_scaling_inert')}} p
    JOIN {{ref('find_mass_table')}} m ON m.runid = p.runid
    WHERE ptype=3
    GROUP BY p.snap, p.runid
)
SELECT
    com2.snap, com2.runid,
    (mtot2 * cx2 + mtot3 * cx3) / (mtot2 + mtot3 + 1.e-13) AS cx,
    (mtot2 * cy2 + mtot3 * cy3) / (mtot2 + mtot3 + 1.e-13) AS cy,
    (mtot2 * cz2 + mtot3 * cz3) / (mtot2 + mtot3 + 1.e-13) AS cz,
    (mtot2 * cvx2 + mtot3 * cvx3) / (mtot2 + mtot3 + 1.e-13) AS cvx,
    (mtot2 * cvy2 + mtot3 * cvy3) / (mtot2 + mtot3 + 1.e-13) AS cvy,
    (mtot2 * cvz2 + mtot3 * cvz3) / (mtot2 + mtot3 + 1.e-13) AS cvz,
    mtot2 + mtot3 AS mtot
FROM com2 JOIN com3
ON com2.snap = com3.snap AND com2.runid = com3.runid