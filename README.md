# kessel

Pipeline for running sets of SMUGGLE galaxy simulations with AREPO. You describe a set of runs in one YAML file, and Kessel generates the initial conditions and submits the jobs, then turns the snapshots into analysis tables and fits emulators to the results.

## Setup

Run these on the cluster from the repo root:

```bash
bash setup.sh
conda activate kessel
```

Then create a `.env` file in the repo root:

```bash
EMAIL=you@example.edu       # SLURM job notifications
S3_BUCKET=my-bucket         # optional, see "Monitoring a set"
```

## Quick start

A sample set of parameters under `my_sample_set` has been included for you. Start by running:

```bash
kessel run my_sample_set
```

Run every `kessel` command from the repo root. `experiments/` isn't tracked by git, so keep your own copy of any params file you care about.

## Commands

| Command | What it does |
|---|---|
| `kessel run <set>` | Submits a SLURM job that generates the runs, submits them to AREPO, and monitors them |
| `kessel restart <set>` | Submits a job that resubmits unfinished runs and monitors them |
| `kessel analyze <set>` | Fits the emulators and makes corner plots |
| `kessel clean <set>` | Deletes the converted parquet files in `simdata/<set>` |
| `kessel dbt run <set>` | Runs dbt once, by hand |
| `kessel dbt prep <set>` | Rewrites and reloads the field schema and seed tables for dbt |

- **`kessel run`:** use this once per set. Running it again on an existing set resubmits every run.
- **`kessel restart`:** only use this when none of the set's AREPO jobs are queued or running, or it will start a second copy of them.
- **`kessel dbt run`:** don't use this while the monitor is running dbt or an upload, because only one can use the database at a time.

## Monitoring a set

The monitor runs as a SLURM job named `kessel`, which does the following:

| When | What |
|---|---|
| Every 30 minutes | Converts new snapshots to parquet in `simdata/<set>` |
| Every 3 hours | Runs dbt to rebuild the tables in `experiments/<set>/dbt.duckdb` |
| 30 minutes after each dbt run | Uploads the tables to `s3://$S3_BUCKET/<set>/` |

## Results

When the runs have finished and dbt has processed them, run:

```bash
kessel analyze <set>
```

The output goes to `experiments/<set>/gpr_fits/`: fits in `projections/` and corner plots in `plots/`.
