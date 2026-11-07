import subprocess

from pathlib import Path

import util.icread as icread

def execute_icgen(cfg):

    p_exe = Path(cfg.paths_arepo.executables.ic_generator).resolve()
    
    exe_name = cfg.icgen_executable_name
    if p_exe.name != exe_name:
        raise RuntimeError("ICGen executable names do not match!")

    p_param = Path(str(cfg.paths_arepo.io_files.icgen_read))

    #print(p_exe, exe_name, p_exe.name)
    subprocess.run([str(p_exe), str(p_param)], cwd=p_exe.parent, check=True)

def convert_icgen_output(cfg):

    pexec = cfg.paths_arepo.executables

    p_icgen_exe = Path(pexec.ic_generator)
    p_arepo_exe = Path(pexec.arepo)

    icgen_root = p_icgen_exe.parent
    arepo_root = p_arepo_exe.parent

    iof = cfg.paths_arepo.io_files
    icgen_makegalaxy_write_rel = Path(iof.icgen_makegalaxy_write)
    arepo_ic_read_rel = Path(iof.arepo_ic_read)

    icgen_write_fullpath = icgen_root / icgen_makegalaxy_write_rel
    arepo_icread_fullpath = arepo_root / arepo_ic_read_rel

    if not icgen_write_fullpath.exists():
        raise FileNotFoundError(
            f"ICGen output not found at: {icgen_write_fullpath}"
        )

    try:
        icread.to_hdf5(
            icgen_write_fullpath,
            arepo_icread_fullpath
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed converting ICGen output "
            f"({icgen_write_fullpath} -> {arepo_icread_fullpath}): {e}"
        ) from e

