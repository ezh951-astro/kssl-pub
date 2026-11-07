# config.py

import os
import re
from pathlib import Path

from dotenv import load_dotenv

from omegaconf import OmegaConf

load_dotenv()
ENV = OmegaConf.create({
    "hpc_user": os.getenv("HPC_USER"),
    "hpc_host": os.getenv("HPC_HOST"),
    "email": os.getenv("EMAIL")
})

def load_global_config(set_name):

    config = OmegaConf.load("settings/config.yaml")
    params = OmegaConf.load(f"experiments/{set_name}/params_of_set.yaml")

    rsset_mandatory = OmegaConf.load("settings/read_snap_settings.yaml").mandatory
    rsset_optional  = params.get('snapshot_fields_optional') or []
    read_snap_settings = OmegaConf.merge({'mandatory': rsset_mandatory}, 
                                         {'optional': rsset_optional})

    print(read_snap_settings)

    cfg = OmegaConf.merge(config, 
                          params,
                          {"read_snap_settings": read_snap_settings},
                          {"env": ENV},
                          {"set_name": set_name})

    return cfg

def load_existing_run_config_from_id(set_name, runid):

    global_config = OmegaConf.load("settings/config.yaml")
    global_config = OmegaConf.merge(global_config, {"set_name": set_name}, {"runid": runid})

    run_config_path = Path(global_config.paths_kessel.run_states) / f"runconfig_{runid}.yaml"

    cfg = OmegaConf.load(run_config_path)
    cfg = OmegaConf.merge(cfg, {"env": ENV})

    return cfg

def load_existing_run_config_from_path(path):

    cfg = OmegaConf.load(path)
    cfg = OmegaConf.merge(cfg, {"env": ENV})

    return cfg   

def save_run_config(cfg):

    missing = [k for k in ("runid", "n_runs") if k not in cfg]
    if missing:
        raise KeyError(f"config is missing required key(s): {', '.join(missing)}")

    path = Path(cfg.paths_kessel.run_states) / f"runconfig_{cfg.runid}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)   # OmegaConf.save won't create folders

    data = OmegaConf.to_container(cfg, resolve=True)
    data.pop("env", None)
    OmegaConf.save(OmegaConf.create(data), path)

def obtain_all_generated_run_cfg_paths(set_name):

    global_config = load_global_config(set_name)
    run_state_path = Path(global_config.paths_kessel.run_states)
    runconfig_re = re.compile(r"^runconfig_(.+)\.yaml$")

    return sorted(p for p in run_state_path.iterdir() if runconfig_re.match(p.name))

###

def create_directories(cfg):

    icgen_root = Path(cfg.paths_arepo.executables.ic_generator).parent
    arepo_root = Path(cfg.paths_arepo.executables.arepo).parent

    iopaths = cfg.paths_arepo.io_files

    def _make_parents(root, name, is_directory=False):

        if is_directory:
            (root/iopaths[name]).mkdir(parents=True, exist_ok=True)
        else:
            (root/iopaths[name]).parent.mkdir(parents=True, exist_ok=True)

    _make_parents(icgen_root, 'icgen_read')
    _make_parents(icgen_root, 'icgen_makegalaxy_write')

    _make_parents(arepo_root, 'arepo_ic_read')
    _make_parents(arepo_root, 'arepo_param_read')
    _make_parents(arepo_root, 'arepo_job_submit')
    _make_parents(arepo_root, 'arepo_snapshot_write', is_directory=True)
    _make_parents(arepo_root, 'arepo_usedparams_write') # technically not needed?

    _make_parents(arepo_root, 'arepo_outputlog_write')
    _make_parents(arepo_root, 'arepo_errorlog_write')

    abs_outputpath_fordbt = Path(cfg.paths_kessel.source_from_sims_for_dbt).resolve()
    abs_outputpath_fordbt.mkdir(parents=True, exist_ok=True)

    Path(cfg.paths_dbt.duckdb).parent.mkdir(parents=True, exist_ok=True)
    Path(cfg.paths_dbt.target).parent.mkdir(parents=True, exist_ok=True)
    Path(cfg.paths_dbt.log).parent.mkdir(parents=True, exist_ok=True)

    gpr_fits_dir = Path(cfg.paths_kessel.gpr_fits)
    (gpr_fits_dir / 'projections').mkdir(parents=True, exist_ok=True)
    (gpr_fits_dir / 'plots').mkdir(parents=True, exist_ok=True)