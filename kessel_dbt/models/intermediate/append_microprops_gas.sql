SELECT *,
  4.0 / ( 3.0*0.76 + 1.0 + 4.0*0.76*Ne ) AS mu,
  5.0/3.0 AS gamma
FROM {{ref('append_cgsqts_gas')}}