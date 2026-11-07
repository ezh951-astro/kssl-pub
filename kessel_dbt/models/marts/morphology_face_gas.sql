{% set xmin = -var('gas_box_length') / 2.0 %}
{% set xmax = var('gas_box_length') / 2.0 %}
{% set xpixels = var('morphology_pixels') %}
{% set ymin = -var('gas_box_length') / 2.0 %}
{% set ymax = var('gas_box_length') / 2.0 %}
{% set ypixels = var('morphology_pixels') %}

SELECT
    p.runid, p.snap,
    CAST(
        LEAST(FLOOR((p.x - {{ xmin }}) / ({{ xmax }} - {{ xmin }}) * {{ xpixels }}), {{ xpixels }} - 1)
    AS INT) AS binx,
    CAST(
        LEAST(FLOOR((p.y - {{ ymin }}) / ({{ ymax }} - {{ ymin }}) * {{ ypixels }}), {{ ypixels }} - 1)
    AS INT) AS biny,
    LOG10(NULLIF(SUM(p.m), 0)) AS value
FROM {{ ref('cast_final_table_gas') }} p
WHERE p.x between {{ xmin }} and {{ xmax }}
AND p.y between {{ ymin }} and {{ ymax }}
GROUP BY binx, biny, runid, snap