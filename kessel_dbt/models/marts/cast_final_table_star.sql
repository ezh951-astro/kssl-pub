{% set cols = get_column_names_except(ref('append_r2d_star'), ['runid', 'snap', 'ID']) %}

SELECT
    runid, snap, ID,
    {% for c in cols %}
    CAST({{ c }} AS {{ dbt.type_float() }}) AS {{ c }}
    {{ "," if not loop.last }}
    {% endfor %}
FROM {{ ref('append_r2d_star') }}