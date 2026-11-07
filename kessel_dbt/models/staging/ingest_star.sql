SELECT
    snap, runid,
    {% for name in get_particle_attrs(4) %}
    CAST({{ name }} AS {{ get_dbt_dtype(name, 4) }}) AS {{ name }}
    {% if not loop.last %},{% endif %}
    {% endfor %}
FROM {{ source('ingest', 'star') }} s
--WHERE {{ new_snaps_only('s') }}