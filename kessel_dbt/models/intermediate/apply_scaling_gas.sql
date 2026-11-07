SELECT
    pt.snap AS snap, pt.runid as runid,     
    pt.nH AS nH, pt.temperature as temperature
    {% for attr in get_unit_conv_attrs(0) %}
    , pt.{{ attr }} * gfp.{{ attr }} AS {{ attr }}
    {% endfor %}
    {% for attr in get_no_unit_conv_attrs(0) %}
    , pt.{{ attr }} AS {{ attr }}
    {% endfor %}
FROM {{ref('append_phase_properties_gas')}} pt
JOIN {{ref('pivot_conv_fac_gas')}} gfp
ON pt.snap = gfp.snap AND pt.runid = gfp.runid


