SELECT
    runid, snap, r3d, logr3d, m,
    0 AS effptype
FROM {{ref('append_r3d_gas')}}
UNION ALL
SELECT
    p.runid, p.snap, p.r3d, p.logr3d,
    m.mp1 AS m,
    1 AS effptype
FROM {{ref('append_r3d_dark')}} p JOIN {{ref('find_mass_table')}} m ON p.runid = m.runid
UNION ALL
SELECT
    runid, snap, r3d, logr3d, m,
    4 AS effptype
FROM {{ref('append_r3d_star')}}
UNION ALL
SELECT
    p.runid, p.snap, p.r3d, p.logr3d,
    CASE
        WHEN p.ptype = 2 THEN m.mp2
        WHEN p.ptype = 3 THEN m.mp3
        ELSE 0
    END AS m,
    4 AS effptype
FROM {{ref('append_r3d_inert')}} p JOIN {{ref('find_mass_table')}} m ON p.runid = m.runid