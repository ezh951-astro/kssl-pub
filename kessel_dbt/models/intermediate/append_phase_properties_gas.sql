SELECT p.*,
  p.mu * (p.gamma-1) * p.U_cgs * cgs.protonmass / cgs.boltzmann AS temperature,
  0.76 * p.rho_cgs / cgs.protonmass AS nH
FROM {{ref('append_microprops_gas')}} p
CROSS JOIN {{ref('cgs_constants')}} cgs