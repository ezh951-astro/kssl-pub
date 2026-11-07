import os
import subprocess
import time
from pathlib import Path

from omegaconf import OmegaConf

import util.submission_helper as submit

###

def genblock_compute_settings(run_name, cfg) -> str:

    partition_name = cfg.system.partition_name
    cres = cfg.compute.cres
    exclude_nodes = cfg.system.exclude_nodes
    cmem = cfg.compute.cmem
    hours = cfg.compute.hours

    arepo_parent = Path(cfg.paths_arepo.executables.arepo).resolve().parent

    output_dir = arepo_parent / cfg.paths_arepo.io_files.arepo_outputlog_write
    error_dir  = arepo_parent / cfg.paths_arepo.io_files.arepo_errorlog_write

    compute_str = f"#SBATCH -J {run_name}\n"
    compute_str += f"#SBATCH -p {partition_name}\n"
    compute_str += f"#SBATCH --ntasks={cres}\n"
    compute_str += f"#SBATCH --exclude={exclude_nodes}\n"
    compute_str += f"#SBATCH --mem={cmem}gb\n"
    compute_str += f"#SBATCH --time={hours}:00:00\n"
    compute_str += f"#SBATCH -o {output_dir}\n"
    compute_str += f"#SBATCH -e {error_dir}\n"

    return compute_str

def write_slurm_script( cfg: OmegaConf,
                    restart: bool,
                    send_email_notification: bool
):
    
    run_name = submit.get_run_name(cfg.set_name, cfg.runid)

    # Compute and Email
    compute_settings_block = genblock_compute_settings(run_name, cfg)
    email_settings_block = f"#SBATCH --mail-user={cfg.env.email}\n#SBATCH --mail-type=ALL\n"

    # Move to Correct Directory
    relative_path_to_executable = cfg.paths_arepo.executables.arepo # includes the executable itself, splits into directory
    abs_dir_exec, name_exec = submit.get_directory_of_executable(relative_path_to_executable)
    cd_to_pwd_block = f"cd {abs_dir_exec}"

    # Load Modules
    module_names = ["slurm", "openmpi", "hdf5"]
    module_load_block = submit.genblock_module_loads(module_names)

    # Additional Config
    additional_cmds_block = "\n"
    for cmd in cfg.system.cmds_during_script:
        additional_cmds_block += f"{cmd}\n"
    additional_cmds_block += "\n"

    # Run Command
    num_processes = cfg.compute.cres
    paramfile_path = Path(cfg.paths_arepo.io_files.arepo_param_read)
    restart_flag = "1" if restart else ""
    run_command = f"mpirun -np {num_processes} ./{name_exec} {paramfile_path} {restart_flag}"

    # Write the file

    arepo_root = Path(cfg.paths_arepo.executables.arepo).parent
    slurm_script_path = arepo_root / cfg.paths_arepo.io_files.arepo_job_submit
    slurm_script_path.parent.mkdir(parents=True, exist_ok=True) # TODO: change this to just ensure existence
    with open(slurm_script_path, "w") as f:

        f.write("#!/bin/bash -l\n")

        f.write(compute_settings_block)
        if send_email_notification:
            f.write(email_settings_block)
        f.write(module_load_block)
        f.write(cd_to_pwd_block)
        f.write(additional_cmds_block)

        f.write(run_command)
        f.write("\n")

    return slurm_script_path

def submit_arepo_job( cfg: OmegaConf,
                    restart: bool = False,
                    send_email_notification: bool = True
) -> None:

    run_name = submit.get_run_name(cfg.set_name, cfg.runid)

    run_start = time.time()

    slurm_script_path = write_slurm_script(cfg, restart, send_email_notification)

    submit.ensure_freshly_written(slurm_script_path, not_before=run_start)

    subprocess.run(["sbatch", slurm_script_path], check=True)
    submit.ensure_queue_submission(run_name)
    time.sleep(cfg.system.seconds_between_submission)