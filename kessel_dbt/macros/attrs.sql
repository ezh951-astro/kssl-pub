{% macro get_particle_attrs(ptype) %}
    {% set result = dbt_utils.get_column_values(
        table=ref(var('schema_config')),
        column='fieldName',
        where="ptype = " ~ ptype
    ) %}
    {{ return(result if result is not none else []) }}
{% endmacro %}

{% macro get_header_attrs() %}
    {% set result = dbt_utils.get_column_values(
        table=ref('headerconfig'),
        column='headerName'
    ) %}
    {{ return(result if result is not none else []) }}
{% endmacro %}



{% macro get_unit_conv_attrs(ptype) %}
    {% set result = dbt_utils.get_column_values(
        table=ref(var('schema_config')),
        column='fieldName',
        where="ptype = " ~ ptype ~ " AND convertUnits = TRUE"
    ) %}
    {{ return(result if result is not none else []) }}
{% endmacro %}

{% macro get_no_unit_conv_attrs(ptype) %}
    {% set result = dbt_utils.get_column_values(
        table=ref(var('schema_config')),
        column='fieldName',
        where="ptype = " ~ ptype ~ " AND convertUnits = FALSE"
    ) %}
    {{ return(result if result is not none else []) }}
{% endmacro %}

{% macro get_optional_particle_attrs(ptype) %}
    {% set result = dbt_utils.get_column_values(
        table=ref(var('schema_config')),
        column='fieldName',
        where="ptype = " ~ ptype ~ " AND mandatory = FALSE"
    ) %}
    {{ return(result if result is not none else []) }}
{% endmacro %}



{% macro get_column_names_except(relation, except=[]) %}
    {%- set except_lower = except | map('lower') | list -%}
    {%- set names = [] -%}
    {%- for col in adapter.get_columns_in_relation(relation) -%}
        {%- if col.name | lower not in except_lower -%}
            {%- do names.append(col.name) -%}
        {%- endif -%}
    {%- endfor -%}
    {{ return(names) }}
{% endmacro %}