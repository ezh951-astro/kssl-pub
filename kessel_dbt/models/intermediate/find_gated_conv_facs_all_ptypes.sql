WITH comb AS (
    SELECT f.name AS name,
    f.ptype AS ptype,
    f.snap as snap, 
    f.runid runid,
    f.combined_fac AS factor,
    m.convert_units AS convert_units
    FROM {{ref('find_combined_scaling')}} f
    JOIN {{ref('ingest_attribute_meta')}} m
    ON f.name = m.name AND f.ptype = m.ptype AND f.snap = m.snap AND f.runid = m.runid
)
SELECT name, ptype, snap, runid,
    CASE
        WHEN convert_units = TRUE THEN factor
        WHEN convert_units = FALSE THEN 1
        ELSE 1
    END AS gated_factor
FROM comb