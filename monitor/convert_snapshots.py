import os
from pathlib import Path

import numpy as np
import h5py
import pandas as pd

from util.dict_helper import attr_or_default
from util.dtype_helper import get_dtype

from util.check_simulation_status import get_snapdir

PTYPE_NAMES = {0: "gas", 1: "dark", 2: "inert", 3: "inert", 4: "star", 5: "inert", 'head':"header", 'attrs':"attributes"}

###

# TODO: support for multiple-file hdf5s. check zHead for that.

def load_entryconfig_into_df(cfg):

    df_pre = []

    for loadinstr_dict in cfg.read_snap_settings.mandatory:

        df_pre.append({
            'fieldName'     : loadinstr_dict['fieldName'],
            'pType'         : loadinstr_dict['pType'],
            'hdf5Name'      : loadinstr_dict['hdf5Name'],
            'fieldColumn'   : loadinstr_dict.get('fieldColumn'),
            'dType'         : loadinstr_dict.get('dType') or 'float64',
            'convertUnits'  : loadinstr_dict['convertUnits'],
            'mandatory'     : True
        })

    if cfg.read_snap_settings.optional:

        for loadinstr_dict in cfg.read_snap_settings.optional:

            df_pre.append({
                'fieldName'     : loadinstr_dict['fieldName'],
                'pType'         : loadinstr_dict['pType'],
                'hdf5Name'      : loadinstr_dict['hdf5Name'],
                'fieldColumn'   : loadinstr_dict.get('fieldColumn'),
                'dType'         : loadinstr_dict.get('dType') or 'float64',
                'convertUnits'  : loadinstr_dict['convertUnits'],
                'mandatory'     : False
            })            

    df = pd.DataFrame(df_pre)
    df['fieldColumn'] = df['fieldColumn'].astype('Int64')   # must be nullable int i.e. 0, 1, 2, <NA>

    df['dbtType'] = [ get_dtype(dtype, "duckdb") for dtype in df.dType ]

    return df

def save_entryconfig_for_dbt(cfg):

    df_entryconfig = load_entryconfig_into_df(cfg)

    dbt_schema_path = Path(f"kessel_dbt/seeds/schema_configs/schema_{cfg.set_name}.csv")
    df_entryconfig.to_csv(dbt_schema_path, index=False)

    #abs_dbt_src = Path(cfg.paths_kessel.source_from_sims_for_dbt).resolve()
    #df_entryconfig.to_csv(abs_dbt_src)
    #write_to_parquet(df_entryconfig, abs_dbt_src / 'entryconfig_ofset.parquet') #ofset to keep the _### pattern

###

def get_ptcl_dbt_src_dir(cfg, snapid, p):

    if p < 0 or p > 5:
        raise ValueError("Invalid ptype, must be 0 thru 5.")

    runid = cfg.runid
    abs_dbt_src = Path(cfg.paths_kessel.source_from_sims_for_dbt).resolve() # includes runid in cfg by now...

    ptype_names = PTYPE_NAMES

    return Path(abs_dbt_src) / f"{ptype_names[p]}_r{int(runid):03d}_{int(snapid):03d}.parquet"

def get_header_dbt_src_dir(cfg, snapid):

    runid = cfg.runid
    abs_dbt_src = Path(cfg.paths_kessel.source_from_sims_for_dbt).resolve()

    return Path(abs_dbt_src) / f"header_r{int(runid):03d}_{int(snapid):03d}.parquet"

def get_attributes_dbt_src_dir(cfg, snapid):

    runid = cfg.runid
    abs_dbt_src = Path(cfg.paths_kessel.source_from_sims_for_dbt).resolve()

    return Path(abs_dbt_src) / f"attributes_r{int(runid):03d}_{int(snapid):03d}.parquet"

###

def write_to_parquet(df, pth):
    
    pth = Path(pth)
    pth_tmp = pth.with_name(pth.name + ".tmp")

    try:
        df.to_parquet(
            pth_tmp,
            engine="pyarrow",
            compression="snappy",
            index=False,
        )
        os.replace(pth_tmp, pth)  # atomic, raises on failure

    except BaseException:
        pth_tmp.unlink(missing_ok=True)
        raise



def extract_snapshot(snapdir, entryconfig):

    def _get_df_of_ptype(f, pType):

        pstr = f"PartType{pType}"
        rows = entryconfig[entryconfig.pType == pType]   # filter once
        has_group = pstr in f

        data = {}
        for row in rows.itertuples():
            if not has_group:
                data[row.fieldName] = np.array([], dtype=row.dType)
            elif pd.isna(row.fieldColumn):
                data[row.fieldName] = np.asarray(f[pstr][row.hdf5Name], dtype=row.dType)
            else:
                col = int(row.fieldColumn)
                data[row.fieldName] = np.asarray(f[pstr][row.hdf5Name][:, col], dtype=row.dType) # slice on the HDF5 dataset itself

        df = pd.DataFrame(data)

        if df.empty:
            fill = {"m": 1.e-13, "x": 0, "y": 0, "z": 0, "vx": 0, "vy": 0, "vz": 0}
            df = pd.DataFrame([fill], columns=df.columns)

        return df.astype({r.fieldName: get_dtype(r.dType, "pandas") for r in rows.itertuples()})

    def _get_df_of_header(f):

        header_attrs = f[u'Header'].attrs

        #record = {
        #    'cf_aTime': header_attrs[u'Time'],
        #    'UnitLength_in_cm': header_attrs[u'UnitLength_in_cm'],
        #    'UnitMass_in_g': header_attrs[u'UnitMass_in_g'],
        #    'UnitVelocity_in_cms': header_attrs[u'UnitVelocity_in_cm_per_s'],

        #    'z': header_attrs[u'Redshift'],
        #    'h_small': header_attrs[u'HubbleParam'],
        #    'omega_matter': header_attrs[u'Omega0']
        #} # hardcoded this from headerconfig; I think we'll just keep it this way from now as a base assumption.

        record = {
            'cf_aTime':            attr_or_default(header_attrs, u'Time', 1.0),
            'UnitLength_in_cm':    attr_or_default(header_attrs, u'UnitLength_in_cm', 3.085678e21),   # default kpc
            'UnitMass_in_g':       attr_or_default(header_attrs, u'UnitMass_in_g', 1.989e43),         # default 1.e10 Msun
            'UnitVelocity_in_cms': attr_or_default(header_attrs, u'UnitVelocity_in_cm_per_s', 1.0e5), # default km/s
            'm_p1': header_attrs[u'MassTable'][1],
            'm_p2': header_attrs[u'MassTable'][2],
            'm_p3': header_attrs[u'MassTable'][3],
            'm_p5': header_attrs[u'MassTable'][5],
            'z':                   attr_or_default(header_attrs, u'Redshift', 0.0),
            'h_small':             attr_or_default(header_attrs, u'HubbleParam', 1.0),
            'Om0':        attr_or_default(header_attrs, u'Omega0', 0.3 )
        }

        df = pd.DataFrame.from_dict([record])

        return df

    def _get_df_of_attributes(f):

        records = []

        for row in entryconfig.itertuples():

            pstr = f'PartType{row.pType}'

            if pstr in f:
                entry_attrs = f[pstr][row.hdf5Name].attrs
                records.append( {
                    'name': row.fieldName,
                    'ptype': row.pType,
                    'convert_units': row.convertUnits,
                    'a_scaling': entry_attrs[u'a_scaling'],
                    'h_scaling': entry_attrs[u'h_scaling'],
                    'length_scaling': entry_attrs[u'length_scaling'],
                    'mass_scaling': entry_attrs[u'mass_scaling'],
                    'velocity_scaling': entry_attrs[u'velocity_scaling'],
                    'to_cgs': entry_attrs[u'to_cgs']
                } )
            else: # this means the particle does not yet appear in that snapshot.
                records.append( {
                    'name': row.fieldName,
                    'ptype': row.pType,
                    'convert_units': False, # I think this is OK. In the case where the particle doesn't exist and the base df is empty... don't convert units?
                    'a_scaling': None,
                    'h_scaling': None,
                    'length_scaling': None,
                    'mass_scaling': None,
                    'velocity_scaling': None,
                    'to_cgs': None
                } )

        df = pd.DataFrame(records)

        return df

    with h5py.File(snapdir) as f:

        df0 = _get_df_of_ptype(f, 0)
        df1 = _get_df_of_ptype(f, 1)
        df2 = _get_df_of_ptype(f, 2)
        df3 = _get_df_of_ptype(f, 3)
        df4 = _get_df_of_ptype(f, 4)
        df5 = _get_df_of_ptype(f, 5)

        header = _get_df_of_header(f)

        attributes = _get_df_of_attributes(f)

    return [ df0, df1, df2, df3, df4, df5 ], header, attributes

def convert_snapshot_to_parquet(cfg, snapid):

    runid = cfg.runid

    snapdir = get_snapdir(cfg, snapid)
    entryconfig = load_entryconfig_into_df(cfg) # also need to save config data to dbt?

    df_ptcls, header, attributes = extract_snapshot(snapdir, entryconfig)

    # header and attributes

    header["snap"] = snapid
    header["runid"] = runid

    attributes["snap"] = snapid
    attributes["runid"] = runid

    write_to_parquet(header, get_header_dbt_src_dir(cfg, snapid))
    write_to_parquet(attributes, get_attributes_dbt_src_dir(cfg, snapid))

    # particles

    for pnum in range(6):

        df_ptcls[pnum]["snap"] = snapid
        df_ptcls[pnum]["runid"] = runid

    # gas, dark, stars as normal

    for pnum in [0,1,4]:

        write_to_parquet(df_ptcls[pnum], get_ptcl_dbt_src_dir(cfg, snapid, pnum))

    # inert particles

    df_inert = pd.concat(
        [df_ptcls[2].assign(ptype=2), df_ptcls[3].assign(ptype=3)],
        ignore_index=True,
    )
    write_to_parquet(df_inert, get_ptcl_dbt_src_dir(cfg, snapid, 2)) # where 2 or both work; both inert.


