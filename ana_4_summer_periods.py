import os,sys,glob,time,collections,gc,itertools,timeit
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
sys.path.append('/Users/peterpfleiderer/Documents/Projects/weather_persistence/')
from summer_persistence_analysis import *




in_file='data/tests/tas_Aday_ECHAM6-3-LR_Plus20-Future_CMIP5-MMM-est1_v2-0_run010_period.nc'
tas=da.read_nc(in_file.replace('_period',''))['tas']
tt=np.asarray(tas,np.float)
datevar = num2date(tas.time,units = "days since 1979-01-01 00:00:00",calendar = "proleptic_gregorian")
year=np.array([int(str(date).split("-")[0])	for date in datevar[:]],np.int32)

period=da.read_nc(in_file)
mm=np.asarray(period['period_midpoints']-tas.time[0],np.int32)
ll=np.asarray(period['period_length'],np.int32)
seas=np.asarray(period['period_season'],np.int32)
state=np.asarray(period['period_state'],np.int32)

time0=time.time()
cum_heat,hot_shift,hot_temp,tasX,Ni_new,original_period_id=summer_period_analysis(ll,mm,seas,state,tt,year,len(period.lat),len(period.lon),len(period.period_id))
print time.time()-time0

out_file=in_file.replace('_period','_summer')
if True: os.system('rm '+out_file)
nc_out=Dataset(out_file,'w')
nc_in=Dataset(in_file,'r')
for dname, the_dim in nc_in.dimensions.iteritems():
	if dname in ['lon','lat']:nc_out.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)
nc_out.createDimension('ID', Ni_new)

for v_name, varin in nc_in.variables.iteritems():
	if v_name in ['lon','lat']:
		outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions)
		outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
		outVar[:] = varin[:]

outVar = nc_out.createVariable('cumulated_heat','f',('ID','lat','lon',))
outVar.long_name='sum over temperature of days in period'
outVar[:] = cum_heat[:,:,:]

outVar = nc_out.createVariable('hottest_day_shift','i',('ID','lat','lon',))
outVar.long_name='shift between hottest day in period and middle of period'
outVar[:] = hot_shift[:,:,:]

outVar = nc_out.createVariable('hottest_day_temp','f',('ID','lat','lon',))
outVar.long_name='temperature of hottest day in period'
outVar[:] = hot_temp[:,:,:]

outVar = nc_out.createVariable('period_id','i',('ID','lat','lon',))
outVar.long_name='original period id'
outVar[:] = original_period_id[:,:,:]

outVar = nc_out.createVariable('tasX','f',('ID','lat','lon',))
outVar.long_name='warmest day in the year'
outVar[:] = tasX[:,:,:]

nc_out.close()
nc_in.close()
print time.time()-time0
# for Ni in [1,5,10,100,len(period.period_id)]:
#     print 'cython ',Ni,timeit.repeat('summer_period_analysis(ll,mm,seas,mask,tt,year,Ni,Nx,Ny)', setup="from __main__ import summer_period_analysis,ll,mm,seas,mask,tt,year,Ni,Nx,Ny", repeat=3,number=1)
#
# for Ni in [1,5,10,100,len(period.period_id)]:
#     print 'cython ',Ni,timeit.repeat('summer_period_analysis__(ll,mm,seas,mask,tt,Ni,Nx,Ny)', setup="from __main__ import summer_period_analysis__,ll,mm,seas,mask,tt,Ni,Nx,Ny", repeat=3,number=1)
