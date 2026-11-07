SELECT
    snap, runid,
    SUM(m * x)  / SUM(m) AS cx,
    SUM(m * y)  / SUM(m) AS cy,
    SUM(m * z)  / SUM(m) AS cz,
    SUM(m * vx) / SUM(m) AS cvx,
    SUM(m * vy) / SUM(m) AS cvy,
    SUM(m * vz) / SUM(m) AS cvz,
    SUM(m) AS mtot
FROM {{ref('apply_scaling_gas')}}
GROUP BY snap, runid