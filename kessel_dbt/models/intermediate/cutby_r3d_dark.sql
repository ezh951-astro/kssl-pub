SELECT *
FROM {{ref('append_r3d_dark')}}
WHERE r3d < {{ var('halo_rad') }}