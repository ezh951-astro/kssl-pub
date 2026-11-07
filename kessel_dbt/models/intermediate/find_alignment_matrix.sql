WITH l2info AS (
    SELECT
        *,
        SQRT(Lx*Lx + Ly*Ly + Lz*Lz + 1.e-13) AS Ltot,
        Lx*Lx + Ly*Ly + 1.e-13 AS Lr2
    FROM {{ref('find_ltot')}}
)
SELECT
    snap, runid,
    1.0 + (Lx*Lx) * (Lz-Ltot) / (Lr2 * Ltot) AS r0x,
    Lx * Ly * (Lz - Ltot) / (Lr2 * Ltot) AS r0y,
    0.0 - (Lx / Ltot) AS r0z,
    Lx * Ly * (Lz - Ltot) / (Lr2 * Ltot) AS r1x,
    1.0 + (Ly*Ly) * (Lz-Ltot) / ( Lr2 * Ltot ) AS r1y,
    0.0 - (Ly / Ltot) AS r1z,
    Lx / Ltot AS r2x,
    Ly / Ltot AS r2y,
    Lz / Ltot AS r2z
FROM l2info