import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import xarray 
import seawater as sw
import matplotlib.pyplot as plt
import scipy.ndimage as nd



# load and read the file 
df = pd.read_csv('IsK_14Jan2021_salinity.txt', sep='\t', skiprows=[0,1,2], engine="python")
# combine the date and time column to one
df['Time'] = df.Date + " " + df.Time
# format the joint time/date column according to yyyy-mm-yy hh:mm:ss
df['Time'] = pd.to_datetime(df['Time'], format='%d/%m/%Y %H:%M:%S')

df['z'] = df['Depth(u)']
df['t'] = df['Temp']
df['s'] = df['Sal.']


print(df.columns)                           # print the names of the columns to see what's there
bottom = df['z'].max()               # find the value of the maximum depth - for fun
print(bottom)
where_bottom = df['z'].idxmax()      # find the index of the maximum depth
print(where_bottom)
df = df[0:where_bottom+1]                   # define new datafield only until index with maximum depth
print(df.tail())                            # double check tail of dataset

# delete not relevant columns
del df['Ser']
del df['Meas']
del df['F (�g/l)']
del df['Opt']
del df['Date']
del df['Unnamed: 10']
del df['Unnamed: 11']
del df['Time']                                                 # delete time from data frame to match model input
del df['Density']                                                 # delete density from data frame to match model input
del df['Depth(u)']
del df['Temp']
del df['Sal.']

# add column with latitude in
lat = 78
df['lat'] = pd.Series([lat for x in range(len(df.index))])

# rearrange columns so they match the needed model input
#df = df[df.columns[[3, 1, 0, 5, 4, 2]]]
df = df.reindex(columns= ['z', 't', 's', 'lat'])

# create means over one meter depth
bins = np.arange(0,np.floor_divide(bottom, 1)+2, 1)             # create bins in 1m steps
df['binned depth'] = pd.cut(df['z'], bins)               # sort depth into bins
df=df.groupby('binned depth').mean()                            # group the sorted depths and create mean over bin 
df=df.interpolate()                                             # interpolate to get rid of NaNs
df["z"]=np.arange(0,np.floor_divide(bottom, 1)+1, 1)     # fix depth to 1m steps after they have vanished due to interpolation

df = df.groupby('binned depth').mean().reset_index()            # convert group back to data frame
del df['binned depth']                                          # delete binned depth data frame

###########################################################################
df = df.iloc[:-1,:]
#df['t'] = df[['t']].apply(savgol_filter,  window_length=41, polyorder=3)
sigma=1
N=30
#print(np.diff(sw.dens0(df['s'],df['t'])))
#plt.plot(np.diff(sw.dens0(df['s'],df['t'])),df['z'][:-1])
fig,ax = plt.subplots(1,3)
#ax[0].plot(sw.dens0(df['s'],df['t']),df['z'])
ax[0].plot(df['t'],df['z'])
for i in range(N):
    df['t']=nd.gaussian_filter1d(df['t'],sigma)
ax[0].plot(df['t'],df['z'])
ax[0].set_title("temp")
ax[1].plot(df['s'],df['z'])
for i in range(N):
    df['s']=nd.gaussian_filter1d(df['s'],sigma)
ax[1].plot(df['s'],df['z'])
ax[1].set_title("sal")
ax[2].plot(np.diff(sw.dens0(df['s'],df['s'])),df['z'][:-1])
ax[2].axvline(0,color="black")
ax[2].set_title("diff")

plt.savefig('../plots/testtest.pdf',bbox_inches='tight')
#plt.show()
############################################################################

df.info()
print(df.tail())                            # double check tail of dataset
df=df.interpolate()                                             # interpolate to get rid of NaNs

# save dataframe as netcdf
output_xr = df.to_xarray()
output_xr['lat'] = 78.
output_xr.to_netcdf(path='../input_data/input_januar.nc', mode='w')
print(output_xr)
print(output_xr.t)


