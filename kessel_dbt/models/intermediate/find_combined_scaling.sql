SELECT
    c.name AS name, c.ptype AS ptype,
    c.snap AS snap, c.runid AS runid,
    u.unit_fac * c.cosmo_fac as combined_fac
FROM {{ref('find_cosmo_fac')}} c
JOIN {{ref('find_unit_fac')}} u
ON c.name = u.name AND c.ptype = u.ptype AND c.snap = u.snap AND c.runid = u.runid