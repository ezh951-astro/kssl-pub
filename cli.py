import subprocess
from pathlib import Path
import typer

app = typer.Typer(help="KESSEL simulation pipeline")
dbt_app = typer.Typer(help="dbt commands")
app.add_typer(dbt_app, name="dbt")

@app.command("run")
def app_run(set_name: str):

    #from main import run
    #run(set_name)
    write_slurm_script(set_name, restart=False)
    subprocess.run(["sbatch", f"slurm_logs/{set_name}.sh"], check=True)

@app.command("restart")
def app_restart(set_name: str):

    #from main import restart
    #restart(set_name)
    write_slurm_script(set_name, restart=True)
    subprocess.run(["sbatch", f"slurm_logs/{set_name}.sh"], check=True)

@app.command("analyze")
def app_analyze(set_name: str):

    from flow_analyzer import flow_summarize_trends
    flow_summarize_trends(set_name)

@app.command("clean")
def app_clean(set_name: str):

    parquets_path = Path("simdata") / set_name

    for f in parquets_path.iterdir():
        if f.is_file():
            f.unlink()

###

@dbt_app.command("run")
def appdbt_run(set_name: str):

    from flow_monitor import flow_run_dbt
    flow_run_dbt(set_name)

@dbt_app.command("prep")
def appdbt_seed(set_name: str):

    from flow_monitor import flow_prepare_dbt
    flow_prepare_dbt(set_name)

### ### ### Slurm Material ### ### ###

NTASKS = 8
CMEM = 64
HOURS = 72

def write_slurm_script(set_name: str, hours: int = HOURS, restart: bool = False):

    def _genblock_compute_settings(hours) -> str:

        compute_str  = f"#SBATCH -J kessel\n"
        compute_str += f"#SBATCH -p epyc\n"
        compute_str += f"#SBATCH --nodes=1\n"
        compute_str += f"#SBATCH --ntasks=1\n"
        compute_str += f"#SBATCH --cpus-per-task={NTASKS}\n"
        compute_str += f"#SBATCH --mem={CMEM}gb\n"
        compute_str += f"#SBATCH --time={hours}:00:00\n"
        compute_str += f"#SBATCH -o temp/kessel_{set_name}_%j.out\n"
        compute_str += f"#SBATCH -e temp/kessel_{set_name}_%j.err\n"

        return compute_str

    if restart:
        run_command = f"python main.py -n {set_name} -R"
    else:
        run_command = f"python main.py -n {set_name}"

    with open(f"slurm_logs/{set_name}.sh", "w") as f:

        f.write("#!/bin/bash -l\n")

        f.write(_genblock_compute_settings(hours))

        f.write("module load slurm\n")
        f.write(f"cd {Path.cwd()}\n")
        f.write("conda activate kessel\n")
        f.write("prefect config view\n")

        f.write(run_command)
        f.write("\n")

### ### ###






if __name__ == "__main__":
    app()