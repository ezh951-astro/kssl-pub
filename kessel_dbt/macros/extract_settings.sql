{#
{% macro get_setting(setting_name) %}
    {{ return(dbt_utils.get_column_values(
        table=ref('extraction_settings'),
        column='val',
        where="setting = '" ~ setting_name ~ "'"
    )[0]) }}
{% endmacro %}
#}