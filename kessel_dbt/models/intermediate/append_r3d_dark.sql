SELECT *,
    SQRT(x*x + y*y + z*z) AS r3d,
    LOG(x*x + y*y + z*z) / 2.0 AS logr3d
FROM {{ref('apply_center_dark')}}