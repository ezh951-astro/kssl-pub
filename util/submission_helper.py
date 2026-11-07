import os
import subprocess
import time
import datetime
from pathlib import Path

###

def insert_yaml_block( insertlines, targetfile, location ):

    with open(targetfile, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if location in line: # will insert before location
            lines[i:i] = insertlines
            break

    with open(targetfile, "w") as f:
        f.writelines(lines)

###

def get_run_name(set_name, runid):

    return f"{set_name}_{runid}"

def genblock_module_loads(module_names: list[str]) -> str:

    if not module_names:
        return ""

    block = "\n"
    for module_name in module_names:
        block += f"module load {module_name}\n"
    block += "\n"

    return block

def get_directory_of_executable(relative_path_to_executable: str) -> tuple[Path, str]:

    p = Path(relative_path_to_executable)

    abs_dir_of_executable = p.resolve().parent
    name_of_executable = p.name

    return abs_dir_of_executable, name_of_executable

###

def check_if_recently_generated(path, max_age_seconds=30):
    if not os.path.exists(path):
        raise FileNotFoundError(f"file not found: {path}")
    
    age = datetime.datetime.now() - datetime.datetime.fromtimestamp(os.stat(path).st_mtime)
    
    if age.total_seconds() > max_age_seconds:
        raise RuntimeError(f"file is {age.total_seconds():.1f}s old, expected fresh file")

def ensure_freshly_written(path, not_before):
    if not os.path.exists(path):
        raise FileNotFoundError(f"file not found: {path}")

    mtime = os.stat(path).st_mtime
    if mtime < not_before:
        raise RuntimeError(
            f"{path} has mtime {mtime:.1f} but this run started at "
            f"{not_before:.1f}; script appears stale (not regenerated "
            f"this run)."
        )

def poll_slurm_queue(run_name):

    result = subprocess.run(
        ["squeue", "-u", os.environ["USER"], "--format=%.10i %.30j %.10P %.8u %.2t %.12M %.5D"],
        capture_output=True,
        text=True
    )

    lines = result.stdout.splitlines()
    if len(lines) <= 1:
        return []
    
    header = lines[0].split()

    jobs = [
        dict(zip(header, line.split()))
        for line in lines[1:]
        if line.strip()
    ]

    return next( (job for job in jobs if job["NAME"]==run_name), None )

def ensure_queue_submission(run_name, timeout=60, poll_interval=1.0):

    jobstate = None

    deadline = time.time() + timeout  # seconds
    while jobstate not in ["PD", "R"]:

        if time.time() > deadline:
            raise TimeoutError(f"Job '{run_name}' did not appear in queue within {timeout}s")

        print(f"Waiting for job {run_name} to hit the queue...")

        job = poll_slurm_queue(run_name)
        if job is not None:
            jobstate = job["ST"]

        time.sleep(poll_interval)