import os

from omegaconf import OmegaConf
from prefect import flow, task
from prefect.futures import wait
from prefect.task_runners import ThreadPoolTaskRunner

from config import create_directories, obtain_all_generated_run_cfg_paths, load_existing_run_config_from_path

from initializer.paramfiles_generate import (write_params_from_generation, 
                                             copy_icgen_params_to_makegalaxy, 
                                             copy_arepo_params_to_arepo
)
from initializer.icgen import execute_icgen, convert_icgen_output
from initializer.slurm_submit import submit_arepo_job

from util.check_simulation_status import is_done, has_restartfiles, has_converted_ics

EMAIL_NOTIFICATION = True

# ---------- Initializer Steps ----------

@task(log_prints=True)
def step_create_directories(cfg):
    create_directories(cfg)

@task(log_prints=True)
def step_write_params(cfg):
    write_params_from_generation(cfg)

@task(log_prints=True)
def step_copy_icgen_params(cfg):
    copy_icgen_params_to_makegalaxy(cfg)

@task(log_prints=True)
def step_execute_icgen(cfg):
    execute_icgen(cfg)

@task(log_prints=True)
def step_copy_arepo_params(cfg):
    copy_arepo_params_to_arepo(cfg)

@task(log_prints=True)
def step_convert_icgen_output(cfg):
    convert_icgen_output(cfg)

@task(log_prints=True)
def step_submit_arepo_job(cfg, restart=False, email_notification=EMAIL_NOTIFICATION):
    submit_arepo_job(cfg, restart=restart, send_email_notification=email_notification)


# ---------- Initialize One Run ----------

@task(log_prints=True)
def task_initialize_run(cfg):
    step_create_directories(cfg)
    step_write_params(cfg)
    step_copy_icgen_params(cfg)
    step_execute_icgen(cfg)
    step_copy_arepo_params(cfg)
    step_convert_icgen_output(cfg)
    step_submit_arepo_job(cfg)

@task(log_prints=True)
def task_start_unsubmitted_run(cfg):
    step_submit_arepo_job(cfg, restart=False)

@task(log_prints=True)
def task_restart_run(cfg):
    step_submit_arepo_job(cfg, restart=True)


# ---------- Initialize The Whole Set ----------

@task(log_prints=True)
def task_run_prior_cmds(cfg):
    for cmd in cfg.system.cmds_prior_script:
        #print(f"Performing command '{cmd}'")
        #subprocess.run(cmd, shell=True, check=True)
        os.system(cmd)

###

@flow(task_runner=ThreadPoolTaskRunner(max_workers=8), log_prints=True)
def flow_submit_all_runs(set_name: str):

    run_cfg_paths = obtain_all_generated_run_cfg_paths(set_name)

    first_run_cfg = OmegaConf.load(run_cfg_paths[0])
    task_run_prior_cmds(first_run_cfg) # the first one should contain the info you need

    futures = []
    for run_cfg_path in run_cfg_paths:
        run_cfg = load_existing_run_config_from_path(run_cfg_path)
        futures.append(task_initialize_run.submit(run_cfg))

    wait(futures)

    return [f.result(raise_on_failure=False) for f in futures]

###

@flow(task_runner=ThreadPoolTaskRunner(max_workers=8), log_prints=True)
def flow_resubmit_existing_runs(set_name: str):

    run_cfg_paths = obtain_all_generated_run_cfg_paths(set_name)

    first_run_cfg = OmegaConf.load(run_cfg_paths[0])
    task_run_prior_cmds(first_run_cfg)

    futures = []
    for run_cfg_path in run_cfg_paths:

        run_cfg = load_existing_run_config_from_path(run_cfg_path)

        if not is_done(run_cfg):

            if has_restartfiles(run_cfg):
                futures.append(task_restart_run.submit(run_cfg))
            elif has_converted_ics(run_cfg):
                # you are considered to be unsubmitted if your first restartfile hasnt been written yet
                futures.append(task_start_unsubmitted_run.submit(run_cfg))
            else:
                futures.append(task_initialize_run.submit(run_cfg))

    wait(futures)

    return [f.result(raise_on_failure=False) for f in futures]