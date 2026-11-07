SELECT
    pt.snap AS snap, pt.runid as runid
    {% for attr in get_unit_conv_attrs(4) %}
    , pt.{{ attr }} * gfp.{{ attr }} AS {{ attr }}
    {% endfor %}
    {% for attr in get_no_unit_conv_attrs(4) %}
    , pt.{{ attr }} AS {{ attr }}
    {% endfor %}
FROM {{ref('ingest_star')}} pt
JOIN {{ref('pivot_conv_fac_star')}} gfp
ON pt.snap = gfp.snap AND pt.runid = gfp.runid