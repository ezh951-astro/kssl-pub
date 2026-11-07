"""
Matplotlib Corner-Plot Heatmap Template
========================================
• Lower-triangle panels: 2D heatmap for each pair (i, j), i < j
• Diagonal panels:       independent error-bar curves, one per index
• Bottom:                shared horizontal colorbar for all heatmap panels

Dependencies
------------
    pip install numpy matplotlib

Usage
-----
    python cornerplot_heatmaps.py
"""

from __future__ import annotations
 
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from matplotlib import colormaps

from math import log10, floor
from typing import Optional
 
 
# ─────────────────────────────────────────────────────────────────────────────
def _sig2(v: float) -> str:
    """Format a number to 2 significant figures."""
    if v == 0:
        return "0"
    mag = floor(log10(abs(v)))
    rounded = round(v, -mag + 1)
    return f"{rounded:.0f}" if mag >= 1 else f"{rounded:.{max(0, 1 - mag)}f}"

# ─────────────────────────────────────────────────────────────────────────────
def create_cmap(cmapname,lo=4.0,hi=8.0,Nbins=20):
    
    levels = MaxNLocator(nbins=Nbins).tick_values(lo,hi)
    cmap = plt.get_cmap(cmapname)
    norm = BoundaryNorm(levels,ncolors=cmap.N,clip=True)
    return cmap, norm
 
def corner_heatmap(
    # ── Data ──────────────────────────────────────────────────────────────────
    maps_1D: dict[int, tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]],
    # dict mapping i  →  (x, y, err)  where err may be None
 
    maps_2D: dict[tuple[int, int], tuple[np.ndarray, np.ndarray, np.ndarray]],
    # dict mapping (i, j) with i < j  →  (x_vals, y_vals, 2D array of shape (nx, ny))
 
    labels: list[str],
    # one label per index
 
    # ── Appearance ────────────────────────────────────────────────────────────
    colormap_name: str = "inferno",
    # any matplotlib colormap name
 
    curve_color: str = "#e07b39",
    # color for diagonal error-bar curves
 
    n_color_bins: int = 12,
    # number of discrete colour steps in the heatmap colormap
 
    cbar_label: str = "Value",
    # label shown on the colorbar
 
    figsize: tuple[float, float] = (9, 9),
) -> plt.Figure:
    """
    Draw a corner-plot with 2D heatmaps on the lower triangle and
    error-bar curves on the diagonal.
 
    Parameters
    ----------
    maps_1D : dict {i: (x, y, err)}
        Diagonal data. ``err`` may be None to suppress error bars.
    maps_2D : dict {(i, j): (x_vals, y_vals, 2D array)}
        Off-diagonal data. Keys must satisfy i < j. The 2D array has
        shape ``(nx, ny)`` — rows index the x-coordinate, columns index
        the y-coordinate. It is transposed internally before being
        passed to ``imshow``. Each entry carries its own coordinate
        arrays, allowing a different grid per panel.
    labels : list of str
        Axis labels, one per index.
    colormap_name : str
        Matplotlib colormap name for the heatmaps.
    curve_color : str
        Colour for the diagonal error-bar curves.
    n_color_bins : int
        Number of discrete colour levels.
    cbar_label : str
        Colorbar axis label.
    figsize : (width, height)
        Figure size in inches.
 
    Returns
    -------
    matplotlib.figure.Figure
    """
 
    ndim = len(labels)
 
    # ── Input validation ──────────────────────────────────────────────────────
    assert set(maps_1D.keys()) == set(range(ndim)), (
        f"maps_1D keys {sorted(maps_1D.keys())} "
        f"must be exactly {{0, ..., {ndim - 1}}}"
    )
    for (i, j) in maps_2D:
        assert i < j, (
            f"maps_2D key ({i}, {j}) violates i < j"
        )
        assert 0 <= i < ndim and 0 <= j < ndim, (
            f"maps_2D key ({i}, {j}) is out of range for ndim={ndim}"
        )
 
    # ── Colour normalisation ──────────────────────────────────────────────────
    all_vals = np.concatenate([img.ravel() for _, _, img in maps_2D.values()])
    vmin, vmax = np.nanpercentile(all_vals, [2, 98])
    norm = mcolors.BoundaryNorm(
        boundaries=np.linspace(vmin, vmax, n_color_bins + 1),
        ncolors=n_color_bins,
    )
    # cmap = plt.cm.get_cmap(colormap_name).resampled(n_color_bins) # deprecated
    cmap = colormaps[colormap_name].resampled(n_color_bins)

    # ── Figure / GridSpec ─────────────────────────────────────────────────────
    # `bottom` is computed so that the drawing area is square in inches,
    # which (with hspace=wspace=0) makes every cell square too.
    fig = plt.figure(figsize=figsize)
    left, right, top = 0.10, 0.95, 0.97
    fig_w, fig_h = figsize
    bottom = top - (right - left) * fig_w / fig_h
    gs = gridspec.GridSpec(
        ndim, ndim,
        figure=fig,
        left=left, right=right,
        bottom=bottom, top=top,
        hspace=0.0, wspace=0.0,
    )
 
    # ── Draw panels ───────────────────────────────────────────────────────────
    ax_lookup: dict[tuple[int, int], plt.Axes] = {}
 
    for row in range(ndim):
        for col in range(ndim):
            if col > row:
                continue
 
            ax = fig.add_subplot(gs[row, col])
            ax_lookup[(row, col)] = ax
 
            # ── Diagonal: error-bar curve ─────────────────────────────────────
            if row == col:
                cx, cy, cerr = maps_1D[row]
                ax.errorbar(
                    cx, cy,
                    yerr=cerr if cerr is not None else None,
                    fmt="-o", markersize=3, linewidth=1.2,
                    color=curve_color, ecolor=curve_color,
                    elinewidth=0.8, capsize=2,
                )
                ax.set_xlim(cx[0], cx[-1])
                _c = 0.5 * (vmin + vmax)
                _h = 0.75 * (vmax - vmin)
                ax.set_ylim(_c - _h, _c + _h)
                ax.yaxis.set_label_position("right")
                ax.yaxis.tick_right()
 
            # ── Off-diagonal: 2D heatmap ──────────────────────────────────────
            else:
                _x, _y, img = maps_2D[(col, row)]
                ax.imshow(
                    img.T,
                    origin="lower",
                    aspect="auto",
                    extent=[_x[0], _x[-1], _y[0], _y[-1]],
                    cmap=cmap,
                    norm=norm,
                    interpolation="nearest",
                )
 
            # ── Tick / label hygiene ──────────────────────────────────────────
            if row < ndim - 1:
                ax.set_xticks([])
            else:
                # Bottom row: ticks at 0.2 and 0.8 of the panel's x-range.
                x_lo, x_hi = (cx[0], cx[-1]) if row == col else (_x[0], _x[-1])
                xt = [x_lo + 0.2 * (x_hi - x_lo), x_lo + 0.8 * (x_hi - x_lo)]
                ax.set_xticks(xt)
                ax.set_xticklabels([_sig2(t) for t in xt])
                ax.set_xlabel(labels[col], fontsize=11)
 
            if col > 0:
                if row != col:
                    ax.set_yticks([])
            else:
                if row != col:
                    ax.set_ylabel(labels[row], fontsize=11)
                    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: _sig2(v)))

            # Diagonal: y-ticks at 0.2 and 0.8 of the panel's y-range.
            if row == col:
                y_lo, y_hi = _c - _h, _c + _h
                yt = [y_lo + 0.2 * (y_hi - y_lo), y_lo + 0.8 * (y_hi - y_lo)]
                ax.set_yticks(yt)
                ax.set_yticklabels([_sig2(t) for t in yt])
 
    # ── Flush axis labels ─────────────────────────────────────────────────────
    fig.align_ylabels([ax_lookup[(row, 0)] for row in range(1, ndim)])
    fig.align_xlabels([ax_lookup[(ndim - 1, col)] for col in range(ndim)])
 
    # ── Colorbar ──────────────────────────────────────────────────────────────
    # Sits centred in the reserved strip, well clear of the panel tick labels.
    cbar_y = 0.04 + (bottom - 0.08) / 2
    cbar_ax = fig.add_axes([0.10, cbar_y, 0.85, 0.04])
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal", spacing="uniform")
    cbar.set_label(cbar_label, fontsize=13, labelpad=6)
    cbar.ax.tick_params(labelsize=11)
    cbar.ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: _sig2(v)))
 
    return fig, ax_lookup


# ── Example usage ─────────────────────────────────────────────────────────────
if __name__ == "__main__":

    rng = np.random.default_rng(0)
    NY, NX = 40, 60
    ndim = 4

    def _fake_curve(i):
        x   = np.linspace(0, 1, 30)
        y   = np.sin((i + 1) * np.pi * x) + 0.05 * rng.standard_normal(30)
        err = 0.05 + 0.03 * rng.random(30)
        return x, y, err # tuple of numpy arrays

    def _fake_image(i, j):
        x = np.linspace(0, 2 * np.pi, NX)
        y = np.linspace(0, 2 * np.pi, NY)
        X, Y = np.meshgrid(x, y)
        return np.sin((i + 1) * X) * np.cos((j + 1) * Y) + 0.3 * rng.standard_normal((NY, NX))
    
    def _fake_map2D(i, j):

        return np.linspace(0, 1, NX), np.linspace(0, 1, NY), _fake_image(i,j)

    fig, ax_lookup = corner_heatmap(
        maps_1D         = {i: _fake_curve(i) for i in range(ndim)},
        maps_2D         = {(i, j): _fake_map2D(i, j) for i in range(ndim) for j in range(i + 1, ndim)},
        labels          = [r"$\theta_0$", r"$\theta_1$", r"$\theta_2$", r"$\theta_3$"],
        colormap_name   = "inferno",
        curve_color     = "#e07b39",
        n_color_bins    = 12,
        cbar_label      = "Value",
    )

    ax_lookup[(2, 1)].axhline(0.5, color="white", linestyle="--")
    ax_lookup[(1, 0)].scatter([0.3], [0.7], color="red", s=20, zorder=5)

    #fig.savefig("cornerplot_heatmaps.png", dpi=150, bbox_inches="tight")
    plt.show()
    #print("Saved → cornerplot_heatmaps.png")