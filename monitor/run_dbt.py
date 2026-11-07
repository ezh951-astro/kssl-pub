import json
import subprocess
from pathlib import Path

from prefect_dbt import PrefectDbtRunner, PrefectDbtSettings

from omegaconf import OmegaConf

from util.dict_helper import flags_dict_to_args_list

def run_dbt_noprefect(cfg, flags=None):

    abs_dbt_src = Path(cfg.paths_kessel.source_from_sims_for_dbt).resolve()

    reserved = {"vars", "target-path", "log-path"}
    clash = reserved & set(flags or {})
    if clash:
        raise ValueError(f"run_dbt sets these itself, don't pass them in flags: {clash}")
    flag_args = flags_dict_to_args_list(flags)

    path_duckdb = Path(cfg.paths_dbt.duckdb).resolve()
    path_target = Path(cfg.paths_dbt.target).resolve()
    path_log = Path(cfg.paths_dbt.log).resolve()

    subprocess.run(["dbt", "run", 
                    "--vars", f"{{source_from_sims: {abs_dbt_src}, dbt_duckdb_path: {path_duckdb}}}",
                    "--target-path", str(path_target),
                    "--log-path", str(path_log),
                    *flag_args],
                    cwd = Path('kessel_dbt').resolve(),
                    check=True)






def seed_dbt(cfg, flags=None):

    #abs_dbt_src = Path(cfg.paths_kessel.source_from_sims_for_dbt).resolve()
    dbt_dir = Path("kessel_dbt").resolve()

    reserved = {"select", "vars", "target-path", "log-path"}
    clash = reserved & set(flags or {})
    if clash:
        raise ValueError(f"run_dbt sets these itself, don't pass them in flags: {clash}")
    extra_flag_args = flags_dict_to_args_list(flags)

    runner = PrefectDbtRunner(
        settings=PrefectDbtSettings(project_dir = dbt_dir, profiles_dir = dbt_dir)
    )

    #path_duckdb = Path(cfg.paths_dbt.duckdb).resolve()
    path_target = Path(cfg.paths_dbt.target).resolve()
    path_log = Path(cfg.paths_dbt.log).resolve()

    dbt_vars = get_dbt_vars(cfg)
    seeds = ["path:seeds/shared", f"schema_{cfg.set_name}"]

    #runner.invoke(["seed",
    #                "--select", *seeds,
    #                "--vars", json.dumps(dbt_vars),
    #                "--target-path", str(path_target),
    #                "--log-path", str(path_log),
    #                *flag_args])

    dbt_vars = get_dbt_vars(cfg)
    dbt_flags = [
        "--select", *seeds,
        "--vars", json.dumps(dbt_vars),
        "--target-path", str(path_target),
        "--log-path", str(path_log)
    ]

    runner.invoke(["seed", *dbt_flags, *extra_flag_args])

###

def run_dbt(cfg, flags=None, full_refresh=False):

    dbt_dir = Path("kessel_dbt").resolve()

    reserved = {"vars", "target-path", "log-path"}
    clash = reserved & set(flags or {})
    if clash:
        raise ValueError(f"run_dbt sets these itself, don't pass them in flags: {clash}")
    extra_flag_args = flags_dict_to_args_list(flags)

    runner = PrefectDbtRunner(
        settings=PrefectDbtSettings(project_dir = dbt_dir, profiles_dir = dbt_dir)
    )

    path_target = Path(cfg.paths_dbt.target).resolve()
    path_log = Path(cfg.paths_dbt.log).resolve()

    dbt_vars = get_dbt_vars(cfg)
    dbt_flags = [ 
        "--vars", json.dumps(dbt_vars),
        "--target-path", str(path_target),
        "--log-path", str(path_log)
    ]
    if full_refresh:
        dbt_flags.append("--full-refresh")

    runner.invoke(["run", *dbt_flags, *extra_flag_args])

### ### ###

def get_snapshot_processing_vars(cfg):

    vars = OmegaConf.merge(
        cfg.snapshot_processing,
        #cfg.compute,
        cfg.duration,
        cfg.resolution
    )

    return OmegaConf.to_container(vars, resolve=True)

def get_dbt_vars(cfg):

    abs_dbt_src = Path(cfg.paths_kessel.source_from_sims_for_dbt).resolve()

    path_duckdb = Path(cfg.paths_dbt.duckdb).resolve()

    dbt_vars = {
        "schema_config": f"schema_{cfg.set_name}",
        "source_from_sims": str(abs_dbt_src),
        "dbt_duckdb_path": str(path_duckdb),
        **get_snapshot_processing_vars(cfg)        
    }

    return dbt_vars