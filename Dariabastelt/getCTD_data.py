import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import xarray 
import seawater as sw
import matplotlib.pyplot as plt
from scipy.ndimage import filters

import os
filePath = '../input_data/input_januar.nc'
# As file at filePath is deleted now, so we should check if file exists or not not before deleting them
if os.path.exists(filePath):
    os.remove(filePath)
else:
    print("Can not delete the file as it doesn't exists")




# load and read the file 
df = pd.read_csv('IsK_14Jan2021_salinity.txt', sep='\t', skiprows=[0,1,2], engine="python")
# combine the date and time column to one
df['Time'] = df.Date + " " + df.Time
# format the joint time/date column according to yyyy-mm-yy hh:mm:ss
df['Time'] = pd.to_datetime(df['Time'], format='%d/%m/%Y %H:%M:%S')

df['z'] = df['Depth(u)']
df['t'] = df['Temp']
df['s'] = df['Sal.']


#print(df.columns)                           # print the names of the columns to see what's there
bottom = df['z'].max()               # find the value of the maximum depth - for fun
#print(bottom)
where_bottom = df['z'].idxmax()      # find the index of the maximum depth
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

length = df['t'].shape[0]
N=2
ker_len=41
ker = (1.0/ker_len)*np.ones(ker_len)
start = 65
x = df['z'].to_numpy()[[start,-1]]
y_t = df['t'].to_numpy()[[start,-1]]
y_s = df['s'].to_numpy()[[start,-1]]
m_t,t_t = np.polyfit(x,y_t,deg=1)
m_s,t_s = np.polyfit(x,y_s,deg=1)


fig,ax = plt.subplots(1,4)
#ax[0].plot(sw.dens0(df['s'],df['t']),df['z'])
ax[0].plot(df['t'],df['z'])
#for i in range(N):
#    df['t'] = filters.convolve1d(df['t'], ker)
df['t'][start:] = m_t*df['z'][start:]+t_t
ax[0].plot(df['t'],df['z'])
ax[0].set_title("temp")
ax[1].plot(df['s'],df['z'])
#for i in range(N):
#    df['s'] = filters.convolve1d(df['s'], ker)
df['s'][start:] = m_s*df['s'][start:]+t_s
ax[1].plot(df['s'],df['z'])
ax[1].set_title("sal")
ax[2].plot(sw.dens0(df['s'],df['s']),df['z'])
ax[2].set_title("denS")
ax[3].plot(np.diff(sw.dens0(df['s'],df['s'])),df['z'][:-1])
ax[3].axvline(0,color="black")
ax[3].set_title("dens diff")
print(length)

for i in range(4):
    ax[i].invert_yaxis()
    ax[i].grid(linewidth=.3)

plt.savefig('../plots/testtest.pdf',bbox_inches='tight')
#plt.show()
############################################################################

df.info()
df=df.interpolate()                                             # interpolate to get rid of NaNs

# save dataframe as netcdf
output_xr = df.to_xarray()
output_xr['lat'] = 78.
output_xr.to_netcdf(path='../input_data/input_januar.nc', mode='w')
#print(output_xr)


