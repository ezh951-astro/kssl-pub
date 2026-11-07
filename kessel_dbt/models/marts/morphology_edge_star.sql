{% set xmin = -var('star_box_length') / 2.0 %}
{% set xmax = var('star_box_length') / 2.0 %}
{% set xpixels = var('morphology_pixels') %}
{% set ymin = -var('star_box_length') / 2.0 %}
{% set ymax = var('star_box_length') / 2.0 %}
{% set ypixels = var('morphology_pixels') %}

SELECT
    p.runid, p.snap,
    CAST(
        LEAST(FLOOR((p.y - {{ xmin }}) / ({{ xmax }} - {{ xmin }}) * {{ xpixels }}), {{ xpixels }} - 1)
    AS INT) AS binx,
    CAST(
        LEAST(FLOOR((p.z - {{ ymin }}) / ({{ ymax }} - {{ ymin }}) * {{ ypixels }}), {{ ypixels }} - 1)
    AS INT) AS biny,
    LOG10(NULLIF(SUM(p.m), 0)) AS value
FROM {{ ref('cast_final_table_star') }} p
WHERE p.y between {{ xmin }} and {{ xmax }}
AND p.z between {{ ymin }} and {{ ymax }}
GROUP BY binx, biny, runid, snap