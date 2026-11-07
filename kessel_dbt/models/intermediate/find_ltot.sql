WITH mass_joined_inert AS (
    SELECT
    pi.snap, pi.runid, pi.r3d,
    pi.x AS x, pi.y AS y, pi.z AS z,
    pi.vx AS vx, pi.vy AS vy, pi.vz AS vz,
    CASE
        WHEN pi.ptype = 2 THEN m.mp2
        WHEN pi.ptype = 3 THEN m.mp3
        ELSE 0 -- ensure that only ptypes 2 and 3 are counted towards angular momentum
    END AS m
    FROM {{ref('cutby_r3d_inert')}} pi
    JOIN {{ref('find_mass_table')}} m ON pi.runid = m.runid
),
all_kinematics AS (
        SELECT snap, runid, 
        x,y,z, vx,vy,vz, m 
        FROM {{ref('cutby_r3d_gas')}} 
        WHERE r3d < {{ var('gal_rad') }}
    UNION ALL
        SELECT snap, runid,
        x,y,z, vx,vy,vz, m 
        FROM {{ref('cutby_r3d_star')}} 
        WHERE r3d < {{ var('gal_rad') }}
    UNION ALL
        SELECT snap, runid,
        x,y,z, vx,vy,vz, m
        FROM mass_joined_inert
        WHERE r3d < {{ var('gal_rad') }}
)
SELECT 
    snap, runid,
    SUM(m * (y*vz - z*vy)) AS Lx,
    SUM(m * (z*vx - x*vz)) AS Ly,
    SUM(m * (x*vy - y*vx)) AS Lz
FROM all_kinematics
GROUP BY snap, runid
ORDER BY runid, snap