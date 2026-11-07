#!/usr/bin/env bash
# First-time setup. Run from the repo root.
set -e

conda create -y -n kessel python=3.11

conda run -n kessel pip install -r requirements.txt
conda run -n kessel pip install -e .
conda run -n kessel dbt deps --project-dir kessel_dbt

echo "Done. Activate with: conda activate kessel"
