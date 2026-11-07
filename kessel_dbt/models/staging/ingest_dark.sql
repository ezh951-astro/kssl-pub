SELECT
    snap, runid,
    {% for name in get_particle_attrs(1) %}
    CAST({{ name }} AS {{ get_dbt_dtype(name, 1) }}) AS {{ name }}
    {% if not loop.last %},{% endif %}
    {% endfor %}
FROM {{ source('ingest', 'dark') }} s
--WHERE {{ new_snaps_only('s') }}