SELECT
    snap, runid,
    MAX(CASE WHEN name = 'x' THEN gated_factor END) AS x,
    MAX(CASE WHEN name = 'y' THEN gated_factor END) AS y,
    MAX(CASE WHEN name = 'z' THEN gated_factor END) AS z,   
    MAX(CASE WHEN name = 'vx' THEN gated_factor END) AS vx,
    MAX(CASE WHEN name = 'vy' THEN gated_factor END) AS vy,
    MAX(CASE WHEN name = 'vz' THEN gated_factor END) AS vz
FROM {{ref('find_gated_conv_facs_all_ptypes')}}
WHERE ptype = 2              -- 3 works too, but need to pick one. 
GROUP BY snap, runid