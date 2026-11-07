{{ config(materialized='table') }}

SELECT
    cgs.grav 
        / POWER( u.dist_fac, 1 ) 
        / POWER( u.mass_fac, -1 ) 
        / POWER( u.vel_fac, 2 )
    AS grav,
    cgs.light
        / POWER( u.dist_fac, 0 ) 
        / POWER( u.mass_fac, 0 ) 
        / POWER( u.vel_fac, 1 )
    AS light,
    cgs.boltzmann
        / POWER( u.dist_fac, 0 ) 
        / POWER( u.mass_fac, 1 ) 
        / POWER( u.vel_fac, 2 ) -- only the energy dependence, kelvin is kelvin
    AS boltzmann,
    cgs.protonmass
        / POWER( u.dist_fac, 0 ) 
        / POWER( u.mass_fac, 1 ) 
        / POWER( u.vel_fac, 0 )
    AS protonmass
FROM {{ ref('cgs_constants') }} cgs
JOIN {{ref('unit_conversions')}} u
ON u.system_name = '{{ var('unit_system') }}'
LIMIT 1
