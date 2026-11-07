SELECT
    snap, runid,
    {% for name in get_particle_attrs(0) %}
    CAST({{ name }} AS {{ get_dbt_dtype(name, 0) }}) AS {{ name }}
    {% if not loop.last %},{% endif %}
    {% endfor %}
FROM {{ source('ingest', 'gas') }} s
--WHERE {{ new_snaps_only('s') }}