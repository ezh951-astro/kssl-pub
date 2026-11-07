from pathlib import Path

import duckdb
import pandas as pd

GPR_MARTS_DIR = Path("kessel_dbt/models/gpr_marts")

def get_input_output_space(cfg, output_tag, discrete_id):

    inputs = pd.read_csv(cfg.paths_kessel.feature_values)
    outputs = load_mart(cfg, cfg.outputs[output_tag].mart)

    df = inputs.merge(outputs, on="runid")
    df = df[df["discrete_runid"]==discrete_id]
    df = df.sort_values("runid")

    meta = pd.read_csv(cfg.paths_kessel.feature_metadata)
    meta_cts = meta[meta["variation"]=='continuous']
    cts_feats = meta_cts["name"].tolist()

    cols = cts_feats + ["output_value"]

    arr = df[cols].to_numpy()

    input_space = arr[:,:-1]
    output_space = arr[:,-1]

    return input_space, output_space

def load_mart(cfg, mart_name):

    available_marts = sorted(p.stem for p in GPR_MARTS_DIR.glob("*.sql"))
    if mart_name not in available_marts:
        raise ValueError(f"Unknown mart {mart_name!r}; must be one of {available_marts}.")

    path_duckdb = Path(cfg.paths_dbt.duckdb)
    if not path_duckdb.exists():
        raise FileNotFoundError(f"No duckdb at {path_duckdb}; has dbt been run for this set?")

    # read_only so we don't fight dbt for the write lock
    with duckdb.connect(str(path_duckdb), read_only=True) as con:
        df = con.execute(f'SELECT * FROM "{mart_name}"').df()

    if df.shape[1] != 2 or "runid" not in df.columns:
        raise ValueError(
            f"Mart {mart_name!r} must have exactly two columns, one of them 'runid'; "
            f"got {list(df.columns)}."
        )

    value_col = next(c for c in df.columns if c != "runid")
    df = df.rename(columns={value_col: "output_value"})

    return df

def get_gpr_paths(cfg, output_tag, discrete_id):

    gpr_fits_dir = Path(cfg.paths_kessel.gpr_fits)

    fit_path = gpr_fits_dir / 'projections' / f'{output_tag}_disc{discrete_id}.hdf5'
    corner_plot_path = gpr_fits_dir / 'plots' / f'corner_{output_tag}_{cfg.set_name}_disc{discrete_id}.png'

    return fit_path, corner_plot_path