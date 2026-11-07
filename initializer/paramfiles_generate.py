import subprocess
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import sigfig

import warnings
#warnings.filterwarnings("ignore", category=UserWarning)

from initializer.input_space_generate import get_scaling_func, get_resolution_params

class ParamFiles: # path names only, config-agnostic

    def __init__(self, sim_path, ic_path):

        self.base_sim_params = np.array(Path(sim_path).read_text().splitlines(keepends=True))
        self.base_ic_params  = np.array(Path(ic_path).read_text().splitlines(keepends=True))

        self.sim_params = self.base_sim_params.tolist()
        self.ic_params  = self.base_ic_params.tolist()

    def replace_param(self, base_file, param_name, param_value, dtype='float', sigfigs=4):

        if base_file == 'sim':
            flines = self.sim_params
        elif base_file == 'ics':
            flines = self.ic_params
        else:
            raise ValueError("paramlines must be 'sim' or 'ics'")

        if dtype == 'int':
            value_typed = int(float(param_value))
        elif dtype == 'str':
            value_typed = param_value
        else:
            value_typed = sigfig.round(param_value, sigfigs=sigfigs)

        matches = [i for i, txt in enumerate(flines)
                   if (tokens := txt.split()) and tokens[0] == param_name]

        if len(matches) != 1:
            raise ValueError(
                f"{param_name!r} found {len(matches)} times in {base_file} (expected exactly 1)"
            )

        #flines[matches[0]] = '{:<16}{}\n'.format(param_name, value_typed)
        flines[matches[0]] = f"{param_name}{' ' * 5}{value_typed}\n"

    def write_to_disk(self, modified_sim_param_path, modified_ic_param_path):

        for p in (modified_sim_param_path, modified_ic_param_path):
            Path(p).parent.mkdir(parents=True, exist_ok=True)

        Path(modified_sim_param_path).write_text(''.join(self.sim_params))
        Path(modified_ic_param_path).write_text(''.join(self.ic_params))

###

def write_params_from_generation(cfg):

    # load pre-calculated features
    feature_metadata = pd.read_csv(cfg.paths_kessel.feature_metadata)
    input_space = pd.read_csv(cfg.paths_kessel.feature_values, index_col=0)

    param_names = feature_metadata["param_name"].tolist()
    scaling_of_feats = feature_metadata["scaling"].tolist()
    base_file_of_feats = feature_metadata["base_file"].tolist()
    dtype_of_feats = feature_metadata["dtype"].tolist()

    #input_feat_values = input_space.loc[cfg.runid].tolist()
    input_feat_values = input_space.loc[cfg.runid]
    input_feat_values_ordered = input_feat_values[feature_metadata["name"]].tolist()

    # initialize ParamFiles class
    base_param_paths = cfg.inputs.base_paramfiles
    paramfiles = ParamFiles(
        sim_path = base_param_paths.sim,
        ic_path = base_param_paths.ics
    )

    # replace standard features
    for param_name, input_feat_value, scaling, base_file, dtype in zip(param_names,
                                                            input_feat_values_ordered,
                                                            scaling_of_feats,
                                                            base_file_of_feats,
                                                            dtype_of_feats):

        scaling_func = get_scaling_func(scaling)
        paramfiles.replace_param(base_file,
                                 param_name,
                                 scaling_func(input_feat_value),
                                 dtype=dtype,
                                 sigfigs=cfg.inputs.default_sig_figs_params)

    # replace resolution-based params
    resolution_params = get_resolution_params()
    for key, res_param_value in resolution_params.items():
        paramfiles.replace_param('ics', key, res_param_value, dtype='int')

    # TODO: may also need to replace the target resolution in the paramfile
    # TODO: Some mechanism of estimating M200 from V200 (and R200)?

    # replace output paths
    iopaths = cfg.paths_arepo.io_files
    ic_out = Path(iopaths.icgen_makegalaxy_write)

    paramfiles.replace_param('ics', 'OutputDir',    f"./{ic_out.parent}", dtype='str') # ./ may be necessary for the executable
    paramfiles.replace_param('ics', 'OutputFile',   ic_out.name,   dtype='str' )
    paramfiles.replace_param('sim', 'InitCondFile', process_arepo_ic_read(iopaths.arepo_ic_read), dtype='str')
    paramfiles.replace_param('sim', 'OutputDir',    iopaths.arepo_snapshot_write, dtype='str' )

    # write to experiments folder
    dest_param_paths = cfg.paths_kessel.simulation_params_generated

    dest_modified_sim_param_path = Path(dest_param_paths.sim) / f"{cfg.runid}.txt"
    dest_modified_ics_param_path = Path(dest_param_paths.ics) / f"{cfg.runid}.txt"

    paramfiles.write_to_disk( 
        modified_sim_param_path = dest_modified_sim_param_path,
        modified_ic_param_path = dest_modified_ics_param_path
    )

    return dest_modified_sim_param_path, dest_modified_ics_param_path

def copy_icgen_params_to_makegalaxy(cfg):

    ic_param_path_generated = Path(cfg.paths_kessel.simulation_params_generated.ics)
    ic_param_path_generated /= f"{cfg.runid}.txt"

    p_icgen_exe = Path(cfg.paths_arepo.executables.ic_generator)
    icgen_root = p_icgen_exe.parent
    ic_param_path_dest_rel = cfg.paths_arepo.io_files.icgen_read
    ic_param_path_dest = icgen_root / ic_param_path_dest_rel

    ic_param_path_dest.parent.mkdir(parents=True, exist_ok=True)

    #print(f"Copying {ic_param_path_generated} to {ic_param_path_dest}")
    shutil.copy(ic_param_path_generated, ic_param_path_dest)

def copy_arepo_params_to_arepo(cfg):

    arepo_param_path_generated = Path(cfg.paths_kessel.simulation_params_generated.sim)
    arepo_param_path_generated /= f"{cfg.runid}.txt"

    p_arepo_exe = Path(cfg.paths_arepo.executables.arepo)
    arepo_root = p_arepo_exe.parent
    arepo_param_path_dest_rel = cfg.paths_arepo.io_files.arepo_param_read
    arepo_param_path_dest = arepo_root / arepo_param_path_dest_rel

    arepo_param_path_dest.parent.mkdir(parents=True, exist_ok=True)

    #print(f"Copying {arepo_param_path_generated} to {arepo_param_path_dest}")
    shutil.copy(arepo_param_path_generated, arepo_param_path_dest)

###

def process_arepo_ic_read(arepo_ic_read_path):

    if str(arepo_ic_read_path)[-5:] != '.hdf5':
        raise ValueError("Arepo IC Read path must end in .hdf5 to comply with paramfile format.")
    return str(arepo_ic_read_path)[:-5] # removes .hdf5 quirk from paramfile