SELECT *,
    SQRT(x*x + y*y) AS r2d
FROM {{ref('apply_age_star')}}