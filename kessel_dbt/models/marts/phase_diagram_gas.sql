{% set xmin = var('min_log_density') %}
{% set xmax = var('max_log_density') %}
{% set xpixels = var('density_pixels') %}
{% set ymin = var('min_log_temperature') %}
{% set ymax = var('max_log_temperature') %}
{% set ypixels = var('temperature_pixels') %}

SELECT
    p.runid AS runid, p.snap AS snap,
    CAST(
        LEAST(FLOOR(
            (LOG10(p.nH) - {{ xmin }}) / ({{ xmax }} - {{ xmin }}) * {{ xpixels }}
        ), {{ xpixels }} - 1)
    AS INT) AS binx,
    CAST(
        LEAST(FLOOR(
            (LOG10(p.temperature) - {{ ymin }}) / ({{ ymax }} - {{ ymin }}) * {{ ypixels }}
        ), {{ ypixels }} - 1)
    AS INT) AS biny,
    LOG10(NULLIF(SUM(p.m), 0)) AS value
FROM {{ ref('cast_final_table_gas') }} p
WHERE LOG10(p.nH) between {{ xmin }} and {{ xmax }}
AND LOG10(p.temperature) between {{ ymin }} and {{ ymax }}
GROUP BY binx, biny, runid, snap