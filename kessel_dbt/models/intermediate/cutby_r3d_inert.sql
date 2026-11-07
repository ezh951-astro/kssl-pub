SELECT *
FROM {{ref('append_r3d_inert')}}
WHERE r3d < {{ var('halo_rad') }}