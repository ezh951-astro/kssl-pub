SELECT
    {% for c in get_column_names_except(ref('apply_rotation_star'), ['tForm']) %} {{c}}, {% endfor %}
    tForm * 1000. AS tForm
FROM {{ref('apply_rotation_star')}}