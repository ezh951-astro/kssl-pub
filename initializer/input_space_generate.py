from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import qmc

from omegaconf import open_dict

def generate_params_from_config(cfg):

    if cfg.inputs.sampling_method not in ['pointwise', 'grid', 'lhs']:
        raise ValueError("Invalid sampling method. Must be: pointwise, grid, lhs")

    def _discrete_features_generate(cfg):

        # TODO: on empty discrete features, inject a constant feature.

        discrete_feature_settings = cfg.inputs.discrete_features
        discrete_feature_metadata = pd.DataFrame([
            {
                "name":      f["name"],
                "param_name": f["param_name"],
                "scaling":   "linear",
                "base_file": f["param_type"],
                "dtype":     f["dtype"],
                "variation": "discrete"
            } for f in discrete_feature_settings
        ])
        discrete_feature_values = pd.DataFrame({feat['name']: feat['values'] for feat in discrete_feature_settings})

        # Obtain and validate the number of discrete combos
        discrete_feature_num_allowed_values = []

        for feat in discrete_feature_settings:
            print(f"Discrete feature: {feat['name']} has values {feat['values']}")
            discrete_feature_num_allowed_values.append(len(feat['values']))

        if len(set(discrete_feature_num_allowed_values)) != 1:
            raise ValueError("Different number of values specified per discrete feature, please check.")

        n_discrete_combos = discrete_feature_num_allowed_values[0]

        return discrete_feature_metadata, discrete_feature_values, n_discrete_combos

    def _continuous_features_generate(cfg):

        if cfg.inputs.sampling_method == 'pointwise':

            continuous_feature_metadata = pd.DataFrame([])
            continuous_feature_values = pd.DataFrame(index=[0])

            n_continuous_combos = 1

        else:

            continuous_feature_settings = cfg.inputs.continuous_features
            for f in continuous_feature_settings:
                if f['min'] > f['max']:
                    raise ValueError(
                        f"Feature {f['name']!r} has min > max "
                        f"({f['min']} > {f['max']}); invalid range."
                    )
                if f['min'] == f['max']:
                    raise ValueError(
                        f"Feature {f['name']!r} has min == max ({f['min']}); "
                        f"degenerate range not allowed."
                    )
            continuous_feature_metadata = pd.DataFrame([
                {
                    "name":      f["name"],
                    "param_name": f["param_name"],
                    "scaling":   f["scaling"],
                    "base_file": f["param_type"],   # YAML calls it param_type; code wants base_file
                    "dtype":     "float",
                    "variation": "continuous"
                }
                for f in continuous_feature_settings
            ])

            if cfg.inputs.sampling_method == 'grid':

                n_continuous_combos = 1
                for feat in continuous_feature_settings:
                    if 'npoints' not in feat:
                        raise ValueError( f"grid sampling requires 'npoints' on every continuous feature; {feat['name']!r} is missing it." )
                    n_continuous_combos *= feat['npoints']

                continuous_feature_values = sample_inputs_grid(continuous_feature_settings)

            elif cfg.inputs.sampling_method == 'lhs':

                if 'n_lhs_samples' not in cfg.inputs or cfg.inputs.n_lhs_samples < 1:
                    raise ValueError( "lhs sampling requires 'inputs.n_lhs_samples' to be a positive integer." )
                n_continuous_combos = cfg.inputs.n_lhs_samples

                continuous_feature_values = sample_inputs_latin_hypercube(continuous_feature_settings, cfg.inputs.n_lhs_samples, cfg.seed)

        return continuous_feature_metadata, continuous_feature_values, n_continuous_combos

    discrete_feature_metadata, discrete_feature_values, n_discrete_combos = _discrete_features_generate(cfg)
    continuous_feature_metadata, continuous_feature_values, n_continuous_combos = _continuous_features_generate(cfg)

    # keep track of its discrete or continuous combination
    discrete_feature_values["discrete_runid"] = range(len(discrete_feature_values))
    continuous_feature_values["continuous_runid"] = range(len(continuous_feature_values))
    # TODO: initial conditions ID, for identical initial conditions.

    # TODO: Make it so that continuous features is fully ignorable.
    feature_values = continuous_feature_values.merge(discrete_feature_values, how='cross')
    feature_values.index.name = "runid"
    feature_metadata = pd.concat([continuous_feature_metadata, discrete_feature_metadata], ignore_index=True)

    total_runs = n_discrete_combos * n_continuous_combos
    print(f"Calculated {n_discrete_combos} discrete by {n_continuous_combos} continuous combos for input method {cfg.inputs.sampling_method}")
    print(f"Total runs: {total_runs}")


    ### ----- Validate the combined feature values ----- ###

    # the derived total must match what the cross-merge actually produced
    if len(feature_values) != total_runs:
        raise ValueError(
            f"Computed total_runs={total_runs} but feature_values has "
            f"{len(feature_values)} rows for method "
            f"{cfg.inputs.sampling_method!r}."
        )

    id_cols = ["discrete_runid", "continuous_runid"] # TODO: when IC ID's are added, drop those too
    feature_value_cols = feature_values.columns.drop(id_cols)
    n_feature_value_cols = len(feature_value_cols)

    # column/metadata consistency
    if n_feature_value_cols != feature_metadata.shape[0]:
        raise ValueError(
            f"Column/metadata mismatch: feature_values has "
            f"{n_feature_value_cols} columns but feature_metadata has "
            f"{feature_metadata.shape[0]} rows."
        )
    if set(feature_value_cols) != set(feature_metadata['name']):
        raise ValueError(
            f"feature_values columns and feature_metadata names disagree: "
            f"{set(feature_value_cols) ^ set(feature_metadata['name'])}"
        )

    return total_runs, feature_metadata, feature_values



###



def get_scaling_func(scaling):

    if scaling == 'linear':
        return lambda x: x
    elif scaling == 'log':
        return lambda x: 10.**x
    else:
        raise ValueError(f"Unknown scaling {scaling!r}; must be 'linear' or 'log'.")

    # TODO: Custom scaling funcs. Kinda difficult tho

def sample_inputs_latin_hypercube(feature_settings, nsims, seed):

    nfeats = len(feature_settings)
    lhc_sampler = qmc.LatinHypercube( d=nfeats, optimization='lloyd', seed=seed ) # pLo, pMed, pHi | fCGM | ASN, fSN
    values = lhc_sampler.random(nsims) # [nsims, nfeats]

    for i, feat in enumerate(feature_settings):
        values[:,i] *= (feat['max'] - feat['min'])
        values[:,i] += feat['min']
        #scaling_func = get_scaling_func(feat['scaling'])
        #values[:,i] = scaling_func(values[:,i])

    feature_names = [ feat['name'] for feat in feature_settings ]

    df_values = pd.DataFrame(
        values,
        dtype = object,
        columns = feature_names
    )

    return df_values

def sample_inputs_grid(feature_settings):

    def _sample_feature(feat):
        vals = np.linspace(feat['min'], feat['max'], feat['npoints'])
        #return get_scaling_func(feat['scaling'])(vals)
        return vals

    nfeats = len(feature_settings)
    feature_names = [ feat['name'] for feat in feature_settings ]

    if nfeats == 1:
        points = _sample_feature(feature_settings[0]).reshape(-1, 1)

    elif nfeats == 2:
        featx_vals = _sample_feature(feature_settings[0])
        featy_vals = _sample_feature(feature_settings[1])

        featx_grid, featy_grid = np.meshgrid(featx_vals, featy_vals)
        points = np.column_stack([featx_grid.ravel(), featy_grid.ravel()])

    else:
        raise ValueError("Grid sampling is only meant for dim = 1 or 2. Stopping now to prevent infeasible computations")

    df_points = pd.DataFrame(
        points,
        dtype = object,
        columns = feature_names
    )

    return df_points

def get_resolution_params(resolution_estimate = 1.e4, 
                      mvir_estimate = 1.e10, 
                      disk_baryons_to_mvir_estimate = 1.e-2, 
                      bulge_stars_to_mvir_estimate = 1.e-2,
                      disk_gas_to_stars_estimate = 0.5):

    estimated_number_of_particles = mvir_estimate / resolution_estimate
    estimated_number_of_baryon_particles = estimated_number_of_particles * disk_baryons_to_mvir_estimate

    resolution_params_dict = {
        "N_GAS": int(disk_gas_to_stars_estimate * estimated_number_of_baryon_particles),
        "N_DISK": int((1.0 - disk_gas_to_stars_estimate) * estimated_number_of_baryon_particles),
        "N_HALO": int(estimated_number_of_particles), # assumes negligible fraction of non-dark matter
        "N_BULGE": int(bulge_stars_to_mvir_estimate * estimated_number_of_particles)
    }

    return resolution_params_dict