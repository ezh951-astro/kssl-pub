import struct
import numpy as np
import h5py

import os
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"

def to_hdf5(path_in,path_out):

  f = open(path_in,'rb')

  f.seek(0,2)
  bytesinfile = f.tell()

  f.seek(0,0)
  readbytes = f.tell()

  #reading header
  print("Reading header\n")

  s = f.read(4)
  blklen = np.int64(struct.unpack("i", s))[0]

  s = f.read(24)
  npart = np.array(struct.unpack("6i", s))
  print("num part", npart)

  s = f.read(48)
  massarr = np.array(struct.unpack("6d", s))
  print("mass array", massarr)

  s = f.read(8)
  time = struct.unpack("d", s)

  print("time", time)

  s = f.read(8)
  redshift = struct.unpack("d", s)
  print("redshift", redshift)

  s = f.read(4)
  flag_sfr = struct.unpack("i", s)
  print("flag_sfr", flag_sfr)

  s = f.read(4)
  flag_feedback = struct.unpack("i", s)
  print("flag_feedback", flag_feedback)


  s = f.read(24)
  npartTotal = np.array(struct.unpack("6i", s))
  print("npartTotal", npartTotal)

  s = f.read(4)
  flag_cooling = struct.unpack("i", s)

  print("flag_cooling", flag_cooling)

  s = f.read(4)
  num_files = struct.unpack("i", s)
  print("num_files", num_files)

  s = f.read(8)
  BoxSize = struct.unpack("d", s)
  print("BoxSize", BoxSize)

  s = f.read(8)
  Omega0 = struct.unpack("d", s)
  print("Omega=", Omega0)

  s = f.read(8)
  OmegaLambda = struct.unpack("d", s)
  print("OmegaLambda", OmegaLambda)

  s = f.read(8)
  HubbleParam = struct.unpack("d", s)
  print("HubbleParam", HubbleParam)

  s = f.read(4)
  flag_metals = struct.unpack("i", s)[0]
  print("flag_metals", flag_metals)

  s = f.read(4)
  flag_coolscalar = struct.unpack("i", s)[0]
  print("flag_coolscalar", flag_coolscalar)


  f.seek(4+4+blklen, 0)

  readbytes = f.tell()


  #reading positions

  print("")

  #reading positions
  print("\nReading position block")

  s = f.read(4)
  blklen = np.int64(struct.unpack("i", s))[0]

  nentries = blklen//4
  pos = np.fromfile(f, dtype='float32', count=nentries).reshape(npartTotal.sum(), 3)
  s = f.read(4)

  readbytes = f.tell()


  #read velocities

  print("Position block read: bytes", blklen, "entries", nentries, "particles", nentries//3)

  #read velocities
  print("\nReading velocity block")

  s = f.read(4)
  blklen = np.int64(struct.unpack("i", s))[0]

  nentries = blklen//4
  vel = np.fromfile(f, dtype='float32', count=nentries).reshape(npartTotal.sum(), 3)
  s = f.read(4)

  readbytes = f.tell()

  #read IDs

  print("Velocity block read: bytes", blklen, "entries", nentries, "particles", nentries//3)

  #read IDs
  print("\nReading ID block")

  s = f.read(4)
  blklen = np.int64(struct.unpack("i", s))[0]

  nentries = blklen//4
  ids = np.fromfile(f, dtype='int32', count=nentries)
  s = f.read(4)

  readbytes = f.tell()


  print("ID block read: bytes", blklen, "entries", nentries)


  #Only read masses if particles are present AND without an entry
  #in the mass array
  test = np.where((npartTotal) > 0 & (massarr == 0.0))[0]
  #test = np.where((npartTotal) > 0)[0]

  if(len(test) > 0):
    #read masses

    print("\nReading mass block")

    s = f.read(4)
    blklen = np.int64(struct.unpack("i", s))[0]

    nentries = blklen//4
    masses = np.fromfile(f, dtype='float32', count=nentries)
    s = f.read(4)

    readbytes = f.tell()

    print("mass block read: bytes", blklen, "entries", nentries)


  #only read the next blocks if gas is present

  if(npartTotal[0] > 0):
    #read utherm

    print("\nReading utherm block")

    s = f.read(4)
    blklen = np.int64(struct.unpack("i", s))[0]

    nentries = blklen//4
    u = np.fromfile(f, dtype='float32', count=nentries)
    s = f.read(4)
    
    readbytes = f.tell()

    print("utherm block read: bytes", blklen, "entries", nentries)
      
    if(flag_metals > 0):
      
      #read metallicity
      print("\nReading metallicity block")

      s = f.read(4)
      blklen = np.int64(struct.unpack("i", s))[0]

      nentries = blklen//4
      met = np.fromfile(f, dtype='float32', count=nentries)
      s = f.read(4)

      readbytes = f.tell()

      print("Metallicity block read: bytes", blklen, "entries", nentries)

    if(flag_metals > 1):
      #read abundances
      print("\nReading abundance block")

      s = f.read(4)
      blklen = np.int64(struct.unpack("i", s))[0]

      nentries = blklen//4
      abun = np.fromfile(f, dtype='float32', count=nentries).reshape(npartTotal[0], 10)
      s = f.read(4)

      readbytes = f.tell()

      print("Abundance block read: bytes", blklen, "entries", nentries, "particles", nentries//10)

    if(flag_coolscalar > 0):
      
      #read metallicity
      print("\nReading cooling scalar block")

      s = f.read(4)
      blklen = np.int64(struct.unpack("i", s))[0]

      nentries = blklen//4
      coolscalar = np.fromfile(f, dtype='float32', count=nentries)
      s = f.read(4)

      readbytes = f.tell()

      print("Metallicity block read: bytes", blklen, "entries", nentries)

  print("\nRead", readbytes, "out of", bytesinfile, "bytes present in file\n")


  f.close()

  ##Write the IC file in hdf5 format


  #IC = h5py.File( 'ics_corona_rot_bm_medium_fit_scale2_doublemass.hdf5', 'w')    # open/create file
  #IC = h5py.File( 'ICs/ICID.hdf5', 'w')    # open/create file
  IC = h5py.File(path_out, 'w')    # open/create file


  print("Writing snapshot in hdf5 format")



  ## create hdf5 groups
  header = IC.create_group("Header")    # create header group

  ## write header entries
  header.attrs.create("NumPart_ThisFile", npart, dtype='int32')
  header.attrs.create("NumPart_Total", npartTotal, dtype='int32')

  header.attrs.create("NumPart_Total_HighWord", np.zeros(npartTotal.shape,dtype='int32'), dtype='int32')

  header.attrs.create("MassTable", massarr, dtype='float32')
  header.attrs.create("Time", time, dtype='float32')
  header.attrs.create("Redshift", redshift, dtype='float32')
  header.attrs.create("BoxSize", BoxSize, dtype='float32')
  header.attrs.create("NumFilesPerSnapshot", num_files, dtype='int32')
  header.attrs.create("Omega0", Omega0, dtype='float32')

  header.attrs.create("OmegaB", 0, dtype='float32')

  header.attrs.create("OmegaLambda", OmegaLambda, dtype='float32')
  header.attrs.create("HubbleParam", HubbleParam, dtype='float32')
  header.attrs.create("Flag_Sfr", flag_sfr, dtype='int32')
  header.attrs.create("Flag_Cooling", flag_cooling, dtype='int32')
  header.attrs.create("Flag_Metals", flag_metals, dtype='int32')

  header.attrs.create("Flag_StellarAge", 0, dtype='int32')

  header.attrs.create("NumPart_Total_HighWord", np.zeros(npartTotal.shape, dtype='int32'), dtype='int32')
  header.attrs.create("Flag_Metals", flag_metals, dtype='int32')

  header.attrs.create("Flag_Feedback", 0, dtype='int32')
  header.attrs.create("Flag_DoublePrecision", 0, dtype='int32')

  offsets = np.zeros(npartTotal.shape, dtype='int32')
  offsets[1:] = np.cumsum(npartTotal[:-1])

  if(npartTotal[0] > 0):
    part0 = IC.create_group("PartType0")  # create particle group 

    ## write cell data
    part0.create_dataset("ParticleIDs", data=ids[offsets[0]:offsets[0]+npartTotal[0]] )
    part0.create_dataset("Coordinates", data=pos[offsets[0]:offsets[0]+npartTotal[0]])
    part0.create_dataset("Velocities", data=vel[offsets[0]:offsets[0]+npartTotal[0]])
    part0.create_dataset("InternalEnergy", data=u[offsets[0]:offsets[0]+npartTotal[0]])

    if(massarr[0] == 0.0):
      part0.create_dataset("Masses", data=masses[offsets[0]:offsets[0]+npartTotal[0]])

    if(flag_metals > 0):
      part0.create_dataset("GFM_Metallicity", data=met[offsets[0]:offsets[0]+npartTotal[0]])
    if(flag_metals > 1):

      part0.create_dataset("GFM_Metals", data=abun[offsets[0]:offsets[0]+npartTotal[0]])

    if(flag_coolscalar > 0):
      
      part0.create_dataset("Cooling_scalar", data=coolscalar[offsets[0]:offsets[0]+npartTotal[0]])
      

  if(npartTotal[1] > 0):
    part1 = IC.create_group("PartType1")  # create particle group 

    ## write data
    part1.create_dataset("ParticleIDs", data=ids[offsets[1]:offsets[1]+npartTotal[1]] )
    part1.create_dataset("Coordinates", data=pos[offsets[1]:offsets[1]+npartTotal[1]])
    part1.create_dataset("Velocities", data=vel[offsets[1]:offsets[1]+npartTotal[1]])

    if(massarr[1] == 0.0):
      part1.create_dataset("Masses", data=masses[offsets[1]:offsets[1]+npartTotal[1]])

  if(npartTotal[2] > 0):
    part2 = IC.create_group("PartType2")  # create particle group 

    ## write data
    part2.create_dataset("ParticleIDs", data=ids[offsets[2]:offsets[2]+npartTotal[2]] )
    part2.create_dataset("Coordinates", data=pos[offsets[2]:offsets[2]+npartTotal[2]])
    part2.create_dataset("Velocities", data=vel[offsets[2]:offsets[2]+npartTotal[2]])

    if(massarr[2] == 0.0):
      part2.create_dataset("Masses", data=masses[offsets[2]:offsets[2]+npartTotal[2]])

  if(npartTotal[3] > 0):
    part3 = IC.create_group("PartType3")  # create particle group 

    ## write data
    part3.create_dataset("ParticleIDs", data=ids[offsets[3]:offsets[3]+npartTotal[3]] )
    part3.create_dataset("Coordinates", data=pos[offsets[3]:offsets[3]+npartTotal[3]])
    part3.create_dataset("Velocities", data=vel[offsets[3]:offsets[3]+npartTotal[3]])

    if(massarr[3] == 0.0):
      part3.create_dataset("Masses", data=masses[offsets[3]:offsets[3]+npartTotal[3]])

  #if(npartTotal[5] > 0):
  #  part5 = IC.create_group("PartType5")  # create particle group 

  #  ## write data
  #  part5.create_dataset("ParticleIDs", data=ids[offsets[5]:offsets[5]+npartTotal[5]] )
  #  part5.create_dataset("Coordinates", data=pos[offsets[5]:offsets[5]+npartTotal[5]])
  #  part5.create_dataset("Velocities", data=vel[offsets[5]:offsets[5]+npartTotal[5]])
  #  print(vel[offsets[5]:offsets[5]+npartTotal[5]])

  #  part5.create_dataset("Masses", data=massarr[5])

  ## close file
  IC.close()

  print("done!")


