from pathlib import Path

from omegaconf import OmegaConf
from prefect import flow, task

from config import load_global_config, save_run_config

from initializer.input_space_generate import generate_params_from_config

@task(log_prints=True)
def task_generate_and_save_params(glob_cfg):

    n_runs, feature_metadata, feature_values = generate_params_from_config(glob_cfg)

    print(f"TOTAL RUNS: {n_runs}")

    metadata_path = Path(glob_cfg.paths_kessel.feature_metadata)
    values_path = Path(glob_cfg.paths_kessel.feature_values)

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    values_path.parent.mkdir(parents=True, exist_ok=True)

    feature_metadata.to_csv(metadata_path, index=False)
    feature_values.to_csv(values_path, index=True)

    return n_runs


@task(log_prints=True)
def task_save_all_run_configs(glob_cfg, n_runs):

    glob_cfg = OmegaConf.merge(glob_cfg, {"n_runs": n_runs})
    for run_id in range(n_runs):
        run_cfg = OmegaConf.merge(glob_cfg, {"runid": run_id})
        save_run_config(run_cfg)


@flow(log_prints=True)
def flow_generate_all_run_params(set_name: str):

    glob_cfg = load_global_config(set_name)

    n_runs = task_generate_and_save_params(glob_cfg)

    task_save_all_run_configs(glob_cfg, n_runs)

