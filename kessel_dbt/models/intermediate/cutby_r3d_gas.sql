SELECT *
FROM {{ref('append_r3d_gas')}}
WHERE r3d < {{ var('halo_rad') }}