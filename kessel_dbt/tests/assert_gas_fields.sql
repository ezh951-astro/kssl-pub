{% set gas_columns = adapter.get_columns_in_relation(ref('ingest_gas')) | map(attribute='name') | list %}

SELECT fieldName, ptype
FROM {{ ref(var('schema_config')) }}
WHERE ptype = 0
AND fieldName NOT IN (
    {% for col in gas_columns %}
        '{{ col }}'{{ "," if not loop.last }}
    {% endfor %}
)