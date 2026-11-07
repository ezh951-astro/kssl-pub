import time
from datetime import datetime, timedelta, timezone

from omegaconf import OmegaConf

from prefect import flow, task, serve
from prefect.futures import wait
from prefect.task_runners import ThreadPoolTaskRunner
from prefect.flow_engine import run_flow_in_subprocess
from prefect.schedules import Interval

from config import obtain_all_generated_run_cfg_paths, load_existing_run_config_from_path, load_global_config

from monitor.convert_snapshots import save_entryconfig_for_dbt
from monitor.process_batches import no_parquets_yet, all_snapshots_converted, prepare_new_snapshots_for_dbt
from monitor.run_dbt import seed_dbt, run_dbt
from monitor.aws import upload_to_aws

from util.check_simulation_status import is_done, is_not_yet_started

MAX_SNAP_PROCESSORS = 8
SNAP_PROCESSING_SCHEDULE = 1800 # seconds
DBT_SCHEDULE = 10800

UPLOAD_OFFSET = 1800

@task(log_prints=True)
def step_save_entryconfig_for_dbt(cfg):

    save_entryconfig_for_dbt(cfg)

@task(log_prints=True)
def step_prep_snaps_for_dbt(cfg):

    if (is_done(cfg) and all_snapshots_converted(cfg)) or is_not_yet_started(cfg):
        return 0
    
    prepare_new_snapshots_for_dbt(cfg)

@task(log_prints=True)
def step_seed_dbt(cfg):

    seed_dbt(cfg)

@task(log_prints=True)
def step_run_dbt(cfg):

    if no_parquets_yet(cfg):
        return 0

    run_dbt(cfg)

@task(log_prints=True)
def step_upload(cfg):

    upload_to_aws(cfg.set_name)

###

@flow(task_runner=ThreadPoolTaskRunner(max_workers=MAX_SNAP_PROCESSORS),
      log_prints=True
)
def flow_process_snapshots_all_runs(set_name: str):

    run_cfg_paths = obtain_all_generated_run_cfg_paths(set_name)

    futures = []
    for run_cfg_path in run_cfg_paths:
        run_cfg = load_existing_run_config_from_path(run_cfg_path)
        futures.append(step_prep_snaps_for_dbt.submit(run_cfg))

    wait(futures)

    return [f.result(raise_on_failure=False) for f in futures]

@flow(log_prints=True)
def flow_prepare_dbt(set_name: str):

    run_cfg_paths = obtain_all_generated_run_cfg_paths(set_name)

    run_cfg_0 = load_existing_run_config_from_path(run_cfg_paths[0])

    step_save_entryconfig_for_dbt(run_cfg_0)
    step_seed_dbt(run_cfg_0)

@flow(log_prints=True)
def flow_run_dbt(set_name: str):

    # paths_kessel and paths_dbt are not allowed to depend on runid.

    cfg = load_global_config(set_name)
    step_run_dbt(cfg)

@flow(log_prints=True)
def flow_upload_dbt_results(set_name: str):

    cfg = load_global_config(set_name)
    step_upload(cfg)


###

def monitor_and_process_all_runs(set_name: str):

    p = run_flow_in_subprocess(flow_prepare_dbt, parameters={"set_name": set_name})
    p.join()                          # wait for the seed process to exit, releasing its lock
    if p.exitcode != 0:
        raise RuntimeError(f"flow_prepare_dbt failed (exit code {p.exitcode})")

    serve(
        flow_process_snapshots_all_runs.to_deployment(
            name=f"{set_name}-snapshots",
            interval=SNAP_PROCESSING_SCHEDULE,
            parameters={"set_name": set_name},
        ),
        flow_run_dbt.to_deployment(
            name=f"{set_name}-dbt",
            interval=DBT_SCHEDULE,
            parameters={"set_name": set_name},
        ),
        flow_upload_dbt_results.to_deployment(
            name=f"{set_name}-aws",
            schedule=Interval(
                DBT_SCHEDULE,
                anchor_date=datetime.now(timezone.utc) + timedelta(seconds=UPLOAD_OFFSET),
            ),
            parameters={"set_name": set_name},
        ),
        limit=1,
    )