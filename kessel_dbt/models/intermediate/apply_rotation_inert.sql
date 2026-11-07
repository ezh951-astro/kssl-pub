SELECT
    p.snap AS snap, p.runid as runid,
    p.ptype as ptype,
    r.r0x * p.x + r.r0y * p.y + r.r0z * p.z AS x, 
    r.r1x * p.x + r.r1y * p.y + r.r1z * p.z AS y, 
    r.r2x * p.x + r.r2y * p.y + r.r2z * p.z AS z,
    r.r0x * p.vx + r.r0y * p.vy + r.r0z * p.vz AS vx, 
    r.r1x * p.vx + r.r1y * p.vy + r.r1z * p.vz AS vy, 
    r.r2x * p.vx + r.r2y * p.vy + r.r2z * p.vz AS vz,
    p.r3d AS r3d, p.logr3d AS logr3d 
FROM {{ref('cutby_r3d_inert')}} p
JOIN {{ref('find_alignment_matrix')}} r
ON p.snap = r.snap AND p.runid = r.runid