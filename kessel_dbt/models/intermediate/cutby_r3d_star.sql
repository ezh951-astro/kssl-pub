SELECT *
FROM {{ref('append_r3d_star')}}
WHERE r3d < {{ var('halo_rad') }}