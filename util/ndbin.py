import numpy as np
from scipy.stats import binned_statistic_dd

def project_and_marginalize(
    points: np.ndarray,
    values: np.ndarray,
    dims: list[int],
    grid_mins: list[float],
    grid_maxs: list[float],
    grid_size: int = 50,
    stat: str = "mean",
) -> tuple[np.ndarray, list[np.ndarray]]:
    """
    Project LHS samples onto selected dimensions and marginalize over the rest.

    Parameters
    ----------
    points : (N, D) array of sample coordinates in [min_i, max_i]^D
    values : (N,) array of function values at each sample
    dims   : list of d dimension indices to keep (0-indexed)
    grid_size : number of bins per retained dimension (default 50)
    stat   : aggregation statistic over marginalized dims —
             "mean", "median", "sum", "min", "max", or any callable
             accepted by scipy.stats.binned_statistic_dd

    Returns
    -------
    grid   : (grid_size,) * d array of marginalized values
    centers  : list of d center-of-bin arrays, each of length grid_size
    """

    N, D = points.shape

    if points.ndim != 2:
        raise ValueError(f"points must be 2D, got shape {points.shape}")
    if values.shape != (N,):
        raise ValueError(f"values must have shape ({N},), got {values.shape}")
    if not dims:
        raise ValueError("dims must be non-empty")
    if any(d < 0 or d >= D for d in dims):
        raise ValueError(f"All dims must be in [0, {D-1}]")
    if len(set(dims)) != len(dims):
        raise ValueError("dims must not contain duplicates")

    projected = points[:, dims]          # (N, d)
    bins      = [grid_size] * len(dims)
    ranges = [(grid_mins[i], grid_maxs[i]) for i in dims]

    result = binned_statistic_dd(
        projected, values,
        statistic=stat,
        bins=bins,
        range=ranges,
    )

    grid_vals  = np.nan_to_num(result.statistic, nan=0.0)

    edges = result.bin_edges               # list of d arrays
    centers = [(e[:-1] + e[1:]) / 2 for e in edges]

    return grid_vals, centers