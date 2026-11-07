{%- macro safe_int(value, default=0) -%}
    COALESCE(TRY_CAST({{ value }} AS INT), {{ default }})
{%- endmacro -%}

{%- macro safe_float(value, default=0.0) -%}
    COALESCE(TRY_CAST({{ value }} AS DOUBLE), {{ default }})
{%- endmacro -%}

{% macro get_dbt_dtype(name, ptype) %}
    {% if execute %}
        {% set query %}
            select dbtType
            from {{ ref(var('schema_config')) }}
            where fieldName = '{{ name }}'
              and pType = '{{ ptype }}'
            limit 1
        {% endset %}

        {% set results = run_query(query) %}

        {% if results.rows | length == 0 %}
            {{ exceptions.raise_compiler_error("No dbtType found in schema_config for fieldName='" ~ name ~ "', pType='" ~ ptype ~ "'") }}
        {% endif %}

        {{ return(results.columns[0].values()[0]) }}
    {% endif %}
{% endmacro %}