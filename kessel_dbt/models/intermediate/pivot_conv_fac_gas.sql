SELECT
    snap, runid,
    {% for name in get_particle_attrs(0) %}
    MAX(CASE WHEN name = '{{ name }}' THEN gated_factor END) AS {{ name }}
    {% if not loop.last %},{% endif %}
    {% endfor %}
FROM {{ref('find_gated_conv_facs_all_ptypes')}}
WHERE ptype = 0
GROUP BY snap, runid