SELECT
    p.snap AS snap, p.runid as runid,
    r.r0x * p.x + r.r0y * p.y + r.r0z * p.z AS x, 
    r.r1x * p.x + r.r1y * p.y + r.r1z * p.z AS y, 
    r.r2x * p.x + r.r2y * p.y + r.r2z * p.z AS z,
    p.r3d AS r3d, p.logr3d AS logr3d
FROM {{ref('cutby_r3d_dark')}} p
JOIN {{ref('find_alignment_matrix')}} r
ON p.snap = r.snap AND p.runid = r.runid