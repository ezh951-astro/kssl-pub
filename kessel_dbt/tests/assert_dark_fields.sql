{% set dark_columns = adapter.get_columns_in_relation(ref('ingest_dark')) | map(attribute='name') | list %}

SELECT fieldName, ptype
FROM {{ ref(var('schema_config')) }}
WHERE ptype = 1
AND fieldName NOT IN (
    {% for col in dark_columns %}
        '{{ col }}'{{ "," if not loop.last }}
    {% endfor %}
)