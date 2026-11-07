{% set star_columns = adapter.get_columns_in_relation(ref('ingest_star')) | map(attribute='name') | list %}

SELECT fieldName, ptype
FROM {{ ref(var('schema_config')) }}
WHERE ptype = 4
AND fieldName NOT IN (
    {% for col in star_columns %}
        '{{ col }}'{{ "," if not loop.last }}
    {% endfor %}
)