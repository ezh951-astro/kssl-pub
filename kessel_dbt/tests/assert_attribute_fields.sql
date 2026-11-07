SELECT cfg.fieldName, cfg.ptype
FROM {{ ref(var('schema_config')) }} cfg
WHERE NOT EXISTS (
    SELECT 1
    FROM {{ ref('ingest_attribute_meta') }} a
    WHERE a.name = cfg.fieldName
    AND a.ptype = cfg.ptype
)