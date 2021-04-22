import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import xarray 

# load and read the file 
df = pd.read_csv(r'C:\Users\Daria\Git\pwp_python_00\Dariabastelt\IsK_14Jan2021_salinity.txt', sep='\t', skiprows=[0,1,2], engine="python")
# combine the date and time column to one
df['Time'] = df.Date + " " + df.Time
# format the joint time/date column according to yyyy-mm-yy hh:mm:ss
df['Time'] = pd.to_datetime(df['Time'], format='%d/%m/%Y %H:%M:%S')

print(df.columns)                           # print the names of the columns to see what's there
bottom = df['Depth(u)'].max()               # find the value of the maximum depth - for fun
#print(bottom)
where_bottom = df['Depth(u)'].idxmax()      # find the index of the maximum depth
#print(where_bottom)
df = df[0:where_bottom+1]                   # define new datafield only until index with maximum depth
#print(df.tail())                            # double check tail of dataset

# delete not relevant columns
del df['Ser']
del df['Meas']
del df['F (�g/l)']
del df['Opt']
del df['Date']
del df['Unnamed: 10']
del df['Unnamed: 11']


# add column with latitude in
lat = 78
df['Lat'] = pd.Series([lat for x in range(len(df.index))])

# rearrange columns so they match the needed model input
#df = df[df.columns[[3, 1, 0, 5, 4, 2]]]
df = df.reindex(columns= ['Depth(u)', 'Temp', 'Sal.', 'Lat', 'Time', 'Density'])

# create means over one meter depth
bins = np.arange(0,np.floor_divide(bottom, 1)+2, 1)             # create bins in 1m steps
df['binned depth'] = pd.cut(df['Depth(u)'], bins)               # sort depth into bins
df=df.groupby('binned depth').mean()                            # group the sorted depths and create mean over bin 
df=df.interpolate()                                             # interpolate to get rid of NaNs
df["Depth(u)"]=np.arange(0,np.floor_divide(bottom, 1)+1, 1)     # fix depth to 1m steps after they have vanished due to interpolation

df = df.groupby('binned depth').mean().reset_index()            # convert group back to data frame
del df['binned depth']                                          # delete binned depth data frame
#del df['Time']                                                 # delete time from data frame to match model input
#del df['Dens']                                                 # delete density from data frame to match model input

df.info()
print(df.tail())                            # double check tail of dataset

# save dataframe as netcdf
output_xr = df.to_xarray()
output_xr.to_netcdf(path="test.nc", mode='w')