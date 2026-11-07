{% set header_names = get_header_attrs() %}

SELECT
    snap, runid,
    {% for name in header_names %}
    TRY_CAST( {{ name }} AS DOUBLE ) AS "{{ name }}"
    {% if not loop.last %},{% endif %}
    {% endfor %}
FROM {{ source('ingest', 'header') }} s
--WHERE {{ new_snaps_only('s') }}