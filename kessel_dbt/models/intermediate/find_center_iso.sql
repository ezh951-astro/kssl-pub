SELECT
    c4.snap, c4.runid,
    ((cinert.mtot * cinert.cx) + (c4.mtot * c4.cx)) / (cinert.mtot + c4.mtot) AS ctotx,
    ((cinert.mtot * cinert.cy) + (c4.mtot * c4.cy)) / (cinert.mtot + c4.mtot) AS ctoty,
    ((cinert.mtot * cinert.cz) + (c4.mtot * c4.cz)) / (cinert.mtot + c4.mtot) AS ctotz,
    ((cinert.mtot * cinert.cvx) + (c4.mtot * c4.cvx)) / (cinert.mtot + c4.mtot) AS ctotvx,
    ((cinert.mtot * cinert.cvy) + (c4.mtot * c4.cvy)) / (cinert.mtot + c4.mtot) AS ctotvy,
    ((cinert.mtot * cinert.cvz) + (c4.mtot * c4.cvz)) / (cinert.mtot + c4.mtot) AS ctotvz
FROM {{ref('find_com_inert')}} cinert
JOIN {{ref('find_com_star')}} c4
ON cinert.snap = c4.snap AND cinert.runid = c4.runid