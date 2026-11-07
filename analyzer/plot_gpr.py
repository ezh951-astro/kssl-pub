from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

import util.dict_helper as dh
from util.corner_heatmap import corner_heatmap, create_cmap

from analyzer.analyzer_helper import get_gpr_paths

def plot_corner(cfg, output_tag, discrete_id, ndims, 
                *, cmap = "seismic", color = "black", n_color_bins = 12):

    fit_path, _ = get_gpr_paths(cfg, output_tag, discrete_id)
    f = dh.hdf5_to_dict(fit_path)

    data_1D = f[u"1D"]
    def _get_1D_curve(dim):

        xval  = np.array(data_1D[u"gridlocs"][f"{dim}"]["x"])
        means = np.array(data_1D[u"means"][f"{dim}"])
        stds  = np.array(data_1D[u"stds"][f"{dim}"])

        return xval, means, stds

    data_2D = f[u"2D"]
    def _get_2D_map(i,j):
        xvals = np.array(data_2D[u"gridlocs"][f"{i},{j}"]["x"])
        yvals = np.array(data_2D[u"gridlocs"][f"{i},{j}"]["y"])
        means = np.array(data_2D[u"means"][f"{i},{j}"])

        return xvals, yvals, means

    fig, ax_lookup = corner_heatmap(
        maps_1D         = {i: _get_1D_curve(i) for i in range(ndims)},
        maps_2D         = {(i, j): _get_2D_map(i, j) for i in range(ndims) for j in range(i + 1, ndims)},
        labels          = [ feat['name'] for feat in cfg.inputs.continuous_features ],
        colormap_name   = cmap,
        curve_color     = color,
        n_color_bins    = n_color_bins,
        cbar_label      = cfg.outputs[output_tag].plot_label,
        figsize         = (9,10)
    )

    return fig