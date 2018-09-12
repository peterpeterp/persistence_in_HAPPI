import os,sys,glob,time,collections,signal,gc
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import matplotlib.pyplot as plt
import seaborn as sns

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

data_path='data/CAM4-2degree/All-Hist/'

lat_,lon_=54.,37.5

nc_period_check=da.read_nc(data_path+'tas_Aday_CAM4-2degree_All-Hist_est1_v1-0_ens0000_period_check.nc')
nc_period=da.read_nc(data_path+'tas_Aday_CAM4-2degree_All-Hist_est1_v1-0_ens0000_period.nc')

print(nc_period['period_length'].squeeze()[:,lat_,lon_].values[178:200])
print(nc_period_check['period_length'].squeeze()[:,lat_,lon_].values[178:200])
print(np.nansum(np.abs(nc_period['period_length'].squeeze()[:,lat_,lon_].values[:1400])-np.abs(nc_period_check['period_length'].squeeze()[:,lat_,lon_].values[:1400])))

print(nc_period['period_season'].squeeze()[:,lat_,lon_].values[178:200])
print(nc_period_check['period_season'].squeeze()[:,lat_,lon_].values[178:200])
print(np.nansum(np.abs(nc_period['period_season'].squeeze()[:,lat_,lon_].values[:1400])-np.abs(nc_period_check['period_season'].squeeze()[:,lat_,lon_].values[:1400])))

print(nc_period['period_midpoints'].squeeze()[:,lat_,lon_].values[178:200])
print(nc_period_check['period_midpoints'].squeeze()[:,lat_,lon_].values[178:200])
print(np.nansum(np.abs(nc_period['period_midpoints'].squeeze()[:,lat_,lon_].values[:1400])-np.abs(nc_period_check['period_midpoints'].squeeze()[:,lat_,lon_].values[:1400])))


anom_check=da.read_nc(data_path+'tas_Aday_CAM4-2degree_All-Hist_est1_v1-0_ens0000_anom_check.nc')['tas'].squeeze()[:,lat_,lon_]
anom=da.read_nc(data_path+'tas_Aday_CAM4-2degree_All-Hist_est1_v1-0_ens0000_anom.nc')['tas'].squeeze()[:,lat_,lon_]

print(anom[1350.5:1400.5])
print(anom_check[1350.5:1400.5])
print(np.nansum(anom[410.5:3000.5]-anom_check[410.5:3000.5]))

state_check=da.read_nc(data_path+'tas_Aday_CAM4-2degree_All-Hist_est1_v1-0_ens0000_state_check.nc')['state'].squeeze()[:,lat_,lon_]
state=da.read_nc(data_path+'tas_Aday_CAM4-2degree_All-Hist_est1_v1-0_ens0000_state.nc')['state'].squeeze()[:,lat_,lon_]

print(state[1350.5:1400.5])
print(state_check[1350.5:1400.5])
print(state[1350.5:1400.5]-state_check[1350.5:1400.5])
print(np.nansum(state[300.5:1400.5]-state_check[300.5:1400.5]))




print(nc_period['period_length'][:,lat_,lon_].values[nc_period['period_season'][:,lat_,lon_].values==2])
print(nc_period_check['period_length'][:,lat_,lon_].values[nc_period_check['period_season'][:,lat_,lon_].values==2])

print(nc_period['period_length'][:,lat_,lon_].values[np.where((nc_period['period_season'][:,lat_,lon_].values==2) & (nc_period['period_state'][:,lat_,lon_].values==1))[0]])
print(nc_period_check['period_length'][:,lat_,lon_].values[np.where((nc_period_check['period_season'][:,lat_,lon_].values==2) & (nc_period_check['period_state'][:,lat_,lon_].values==1))[0]])

print(np.mean(nc_period['period_length'][:,lat_,lon_].values[np.where((nc_period['period_season'][:,lat_,lon_].values==2) & (nc_period['period_state'][:,lat_,lon_].values==1))[0]]))
print(np.mean(nc_period_check['period_length'][:,lat_,lon_].values[np.where((nc_period_check['period_season'][:,lat_,lon_].values==2) & (nc_period_check['period_state'][:,lat_,lon_].values==1))[0]]))


#
