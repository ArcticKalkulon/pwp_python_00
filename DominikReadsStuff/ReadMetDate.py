import numpy as np
import netCDF4 as nc

metData = nc.Dataset("../input_data/beaufort_met.nc", "r", format="NETCDF4")
print(metData)
print(metData.dimensions)
print(metData.variables)

