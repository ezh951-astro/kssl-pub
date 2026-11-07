{% macro new_snaps_only(alias) %}
  {%- if is_incremental() -%}
    NOT EXISTS (
        SELECT 1 FROM {{ this }} t
        WHERE t.runid = {{ alias }}.runid AND t.snap = {{ alias }}.snap
    )
  {%- else -%}
    true
  {%- endif -%}
{% endmacro %}
