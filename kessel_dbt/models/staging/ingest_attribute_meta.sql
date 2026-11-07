SELECT *
FROM {{ source('ingest', 'attributes') }} s
--WHERE {{ new_snaps_only('s') }}