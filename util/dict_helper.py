import warnings
from pathlib import Path

import numpy as np
import h5py

def dict_to_hdf5(d: dict, path: str | Path) -> None:
    """
    Recursively write a nested dictionary to an HDF5 file.
    - dicts become groups
    - arrays/lists/scalars become datasets

    Values must be numeric arrays/scalars or nested dicts thereof.
    Parent directories are created if they don't exist.
    """
    def _write(group, d):
        for k, v in d.items():
            if isinstance(v, dict):
                _write(group.require_group(k), v)
            else:
                group.create_dataset(k, data=np.asarray(v))

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as f:
        _write(f, d)

def hdf5_to_dict(path: str | Path) -> dict:
    def _read(group):
        return {
            k: _read(v) if isinstance(v, h5py.Group) else v[()]
            for k, v in group.items()
        }
    with h5py.File(path, "r") as f:
        return _read(f)



def flags_dict_to_args_list(flags=None):

    """Turn e.g., {"select": "staging", "full-refresh": True} into
    ["--select", "staging", "--full-refresh"]."""

    args = []
    for name, value in (flags or {}).items():
        if value is False or value is None:
            continue                  # flag switched off, leave it out
        args.append(f"--{name}")
        if value is not True:
            args.append(str(value))   # flag that takes a value
    return args



def attr_or_default(attrs, key, default):

    """Return attrs[key], or default with a warning if the key is missing."""

    if key in attrs:
        return attrs[key]
    else:
        warnings.warn(f"'{key}' missing from header; using default {default!r}", stacklevel=2)
        return default