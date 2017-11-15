import os,sys,glob,time,collections,gc,itertools,timeit
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da

sys.path.append('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/persistence_in_models/')
from cython_function import *

period=da.read_nc('data/tests/tas_Aday_ECHAM6-3-LR_Plus20-Future_CMIP5-MMM-est1_v2-0_run010_period.nc')
tas=da.read_nc('data/tests/tas_Aday_ECHAM6-3-LR_Plus20-Future_CMIP5-MMM-est1_v2-0_run010.nc')['tas']
mm=np.asarray(period['period_midpoints']-tas.time[0],np.int32)
ll=np.asarray(period['period_length'],np.int32)
seas=np.asarray(period['period_season'],np.int32)
tt=np.asarray(tas,np.float)
Nx=len(period.lon)
Ny=len(period.lat)
Ni=len(period.period_id)

mask=da.read_nc('data/tests/landmask_96x192_NA-1.nc')['landmask']
mask[mask!=1]=0
mask=np.asarray(mask,np.int32)

cu,ho=period_analysis_cy(ll,mm,seas,mask,tt,Ni,Nx,Ny)

summary=da.DimArray(axes=[period.period_id,period.lat,period.lon,['cumulative_heat','hottest_day_shift']],dims=['period_id','lat','lon','type'])
summary[:,:,:,'cumulative_heat']=cu
summary[:,:,:,'hottest_day_shift']=ho
ds=da.Dataset({'summary':summary})
ds.write_nc('data/tests/tas_Aday_ECHAM6-3-LR_Plus20-Future_CMIP5-MMM-est1_v2-0_run010_summer.nc', mode='w')

#
# for Ni in [1,5,10,20,400,len(period.period_id)]:
#     print 'cython ',Ni,timeit.repeat('period_analysis_cy(ll,mm,seas,mask,tt,Ni,Nx,Ny)', setup="from __main__ import period_analysis_cy,ll,mm,seas,mask,tt,Ni,Nx,Ny", repeat=3,number=1)
