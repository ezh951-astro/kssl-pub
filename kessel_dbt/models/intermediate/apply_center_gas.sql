SELECT
    p.snap AS snap, p.runid as runid,
    p.x - c.ctotx AS x,
    p.y - c.ctoty AS y,
    p.z - c.ctotz AS z,
    p.vx - c.ctotvx AS vx,
    p.vy - c.ctotvy AS vy,
    p.vz - c.ctotvz AS vz,
    p.m AS m,
    p.rho AS rho, p.U AS U,
    p.Ne AS Ne,
    p.nH AS nH, p.temperature as temperature
    {% for name in get_optional_particle_attrs(0) %}
    , p.{{ name }} AS {{ name }}
    {% endfor %}
FROM {{ref('apply_scaling_gas')}} p
JOIN {{ref('find_center_iso')}} c
ON p.snap = c.snap AND p.runid = c.runid