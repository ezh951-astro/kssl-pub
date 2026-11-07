SELECT
    p.snap AS snap, p.runid as runid,
    p.x - c.ctotx AS x,
    p.y - c.ctoty AS y,
    p.z - c.ctotz AS z,
    p.vx - c.ctotvx AS vx,
    p.vy - c.ctotvy AS vy,
    p.vz - c.ctotvz AS vz,
    p.m AS m,
    p.ID AS ID, p.tForm as tForm
    {% for name in get_optional_particle_attrs(4) %}
    , p.{{ name }} AS {{ name }}
    {% endfor %}
FROM {{ref('apply_scaling_star')}} p
JOIN {{ref('find_center_iso')}} c
ON p.snap = c.snap AND p.runid = c.runid