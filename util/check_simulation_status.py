import time
from pathlib import Path

import h5py

#import util.submission_helper as submit

###

def is_not_yet_started(run_cfg):
    """True if AREPO has not started running this simulation.
    Determined based on the existence of the used param file"""

    used_params_path = (Path(run_cfg.paths_arepo.executables.arepo).parent /
        run_cfg.paths_arepo.io_files.arepo_usedparams_write)

    return not used_params_path.exists()

def is_done(run_cfg):
    """True once the final expected snapshot (snapshot_processing.final_snapshot) exists and is fully written."""

    final_snapshot_number = int(run_cfg.duration.no_snapshots) - 1

    final_snapshot_path = get_snapdir(run_cfg, final_snapshot_number)

    return file_is_stable(final_snapshot_path)

def file_is_stable(pth, min_age_seconds=300):
    """True if a snapshot looks fully written: untouched for min_age_seconds and readable as HDF5.

    The age check catches files AREPO is still writing (mtime keeps moving); the open
    check catches truncated files and, when HDF5 file locking is on, files still held open."""

    pth = Path(pth)
    if not pth.is_file():
        return False

    if time.time() - pth.stat().st_mtime < min_age_seconds:
        return False

    try:
        with h5py.File(pth, "r") as f:
            return "Header" in f
    except OSError:
        return False

###

def is_not_completed_simulation(run_cfg):
    """True if the simulation has not yet written its final snapshot (duration.no_snapshots - 1).
    This says nothing about whether the snapshots have been converted to parquet
    or processed by dbt."""

    return not is_done(run_cfg)

def has_restartfiles(run_cfg):
    """True if the restart file directory (io_files.arepo_restartfiles_write) exists and contains at least one file."""

    restartfiles_dir = (Path(run_cfg.paths_arepo.executables.arepo).parent /
        run_cfg.paths_arepo.io_files.arepo_restartfiles_write)

    if not restartfiles_dir.is_dir():
        return False

    return any(p.is_file() for p in restartfiles_dir.iterdir())

def has_converted_ics(run_cfg):

    ics_pth = (Path(run_cfg.paths_arepo.executables.arepo).parent /
        run_cfg.paths_arepo.io_files.arepo_ic_read)

    return ics_pth.exists()





### ### ###

def get_snapdir(cfg, snapid):

    def _get_istr3(i):         # Assumes that i>=0
        if i<10:
            return '00'+str(i)
        if i>=10 and i<100:
            return '0'+str(i)
        if i>=100:
            return str(i)

    snapshot_output_dir = Path(cfg.paths_arepo.executables.arepo).parent / cfg.paths_arepo.io_files.arepo_snapshot_write

    istr3 = _get_istr3(snapid)
    snapshot_name = f'snapshot_{istr3}.hdf5' # TODO: force it to be like this in the paramfile

    return snapshot_output_dir / snapshot_name