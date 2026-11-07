from pathlib import Path

from prefect import flow, task

import util.dict_helper as dh

from config import load_global_config

from analyzer.fit_gpr import produce_projection
from analyzer.plot_gpr import *
from analyzer.analyzer_helper import get_gpr_paths

N_EMULATOR_SAMPLES = 100000



@task(log_prints=True)
def task_fit_gprs(cfg, holdouts = [4,7,12,13,24], n_samples = N_EMULATOR_SAMPLES):

    output_tags = cfg.outputs.keys()
    n_disc_feats = len(cfg.inputs.discrete_features[0]['values'])

    for discrete_id in range(n_disc_feats):

        for output_tag in output_tags:

            print(f"Now producing projection for {output_tag}")

            fit_projection = produce_projection(cfg, output_tag, discrete_id, n_samples)

            fit_path, _ = get_gpr_paths(cfg, output_tag, discrete_id)
            dh.dict_to_hdf5(fit_projection, fit_path)


@task(log_prints=True)
def task_plot_gprs(cfg):

    plot_path = Path(cfg.paths_kessel.gpr_fits) / 'plots'
    plot_path.mkdir(parents=True, exist_ok=True)

    n_cts_feats = len(cfg.inputs.continuous_features)

    n_disc_feats = len(cfg.inputs.discrete_features[0]['values'])
    for disc_id in range(n_disc_feats):

        for output_tag in cfg.outputs.keys():

            _, corner_plot_path = get_gpr_paths(cfg, output_tag, disc_id)
            corner_plot_path.parent.mkdir(parents=True, exist_ok=True)
            fig = plot_corner(cfg, output_tag, disc_id, n_cts_feats)
            fig.savefig(corner_plot_path)


@flow(log_prints=True)
def flow_summarize_trends(set_name: str):

    glob_cfg = load_global_config(set_name)

    task_fit_gprs(glob_cfg)
    task_plot_gprs(glob_cfg)