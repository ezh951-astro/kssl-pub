# process_batches.py

import re
from pathlib import Path

from util.check_simulation_status import file_is_stable
from monitor.convert_snapshots import PTYPE_NAMES, convert_snapshot_to_parquet

###

def prepare_new_snapshots_for_dbt(cfg):

    new_snapshots = list_new_snapshots(cfg)

    for snapid in new_snapshots:
        convert_snapshot_to_parquet(cfg, snapid)

def all_snapshots_converted(cfg):
    
    return not list_new_snapshots(cfg)

def no_parquets_yet(cfg):
    
    src = Path(cfg.paths_kessel.source_from_sims_for_dbt).resolve()
    return any(not any(src.glob(f"{name}_*.parquet")) for name in set(PTYPE_NAMES.values()))



###

def list_snapshot_numbers(cfg):

    snap_re = re.compile(r"^snapshot_(\d+)(?:\.\d+)?\.hdf5$") # TODO: works for single-snapshot runs. multi-part files would need something else

    directory = Path(cfg.paths_arepo.executables.arepo).parent / cfg.paths_arepo.io_files.arepo_snapshot_write

    numbers = set()
    for path in directory.iterdir():

        match = snap_re.match(path.name)
        if match and file_is_stable(path):
            numbers.add(int(match.group(1)))

    return sorted(numbers)

def list_parquet_numbers(cfg):

    directory = Path(cfg.paths_kessel.source_from_sims_for_dbt).resolve()
    path_names = [ p.name for p in directory.iterdir() ]

    per_type = []
    for pname in PTYPE_NAMES.values():

        parquet_re = re.compile(rf"^{pname}_r{int(cfg.runid):03d}_(\d+)\.parquet$")

        numbers = set()
        for path_name in path_names:

            match = parquet_re.match(path_name)
            if match:
                numbers.add(int(match.group(1)))

        per_type.append(numbers)

    common = set.intersection(*per_type) if per_type else set()

    return sorted(common)

def list_new_snapshots(cfg):

    snapshot_nums   = list_snapshot_numbers(cfg)
    parquet_nums    = list_parquet_numbers(cfg)

    new_snapshots = sorted(set(snapshot_nums) - set(parquet_nums))

    return new_snapshots