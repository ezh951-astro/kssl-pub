SELECT *
FROM {{ source('ingest', 'inert') }} s
--WHERE {{ new_snaps_only('s') }}