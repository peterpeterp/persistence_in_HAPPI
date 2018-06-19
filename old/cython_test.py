import os,sys,glob,time,collections,gc,itertools,timeit
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da

sys.path.append('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/persistence_in_models/')
import cython_function

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
sys.path.append('/Users/peterpfleiderer/Documents/Projects/weather_persistence/')
from persistence_functions import *

period=da.read_nc('data/tests/tas_Aday_ECHAM6-3-LR_Plus20-Future_CMIP5-MMM-est1_v2-0_run010_period.nc')
tas=da.read_nc('data/tests/tas_Aday_ECHAM6-3-LR_Plus20-Future_CMIP5-MMM-est1_v2-0_run010.nc')['tas']

mask=da.read_nc('data/tests/landmask_96x192_NA-1.nc')['landmask']
mask[mask!=1]=0
mask=np.asarray(mask,np.int32)
# land_yx=[(period.lat[np.argmin(abs(lat-period.lat))],period.lon[np.argmin(abs(lon-period.lon))]) for lat,lon in itertools.product(mask.lat,mask.lon) if mask[lat,lon]==1]
# coord=np.array([(np.argmin(abs(lat-period.lat)),np.argmin(abs(lon-period.lon))) for lat,lon in itertools.product(mask.lat,mask.lon) if mask[lat,lon]==1],np.int32)

# Ni=len(period.period_id)
# Ny=len(period.lat)
# Nx=len(period.lon)
# periods_of_interest=np.array([[i,y,x] for i,y,x in itertools.product(range(Ni),range(Ny),range(Nx)) if period['period_season'].ix[i,y,x]==1])


def period_analysis_py(ids,lats_lons):
    for i,y,x in itertools.product(range(Ni),range(Ny),range(Nx)):
        ll=period['period_length'][per_id,lat_lon[0],lat_lon[1]]
        if ll>0 & period['period_season'][per_id,lat_lon[0],lat_lon[1]]==1:
            mm=period['period_midpoints'][per_id,lat_lon[0],lat_lon[1]]
            days=np.arange(mm-int(abs(ll)/2.),mm+round(abs(ll)/2.),1)
            summary_[per_id,lat_lon[0],lat_lon[1],'cumulative_heat']=np.nansum(tas[days,lat_lon[0],lat_lon[1]])
            summary_[per_id,lat_lon[0],lat_lon[1],'hottest_day_shift']=days[np.nanargmax(np.array(tas[days,lat_lon[0],lat_lon[1]]).flatten())]-mm
    return  summary_





sys.path.append('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/persistence_in_models/')
from cython_function import *

mm=np.asarray(period['period_midpoints']-tas.time[0],np.int32)
ll=np.asarray(period['period_length'],np.int32)
seas=np.asarray(period['period_season'],np.int32)
tt=np.asarray(tas,np.float)
Nx=len(tas.lon)
Ny=len(tas.lat)
Ni=len(period.period_id)



for Ni in [1,5,10,100]:
    print 'cython ',Ni,timeit.repeat('period_analysis_cy(ll,mm,seas,mask,tt,Ni,Nx,Ny)', setup="from __main__ import period_analysis_cy,ll,mm,seas,mask,tt,Ni,Nx,Ny", repeat=3,number=1)


for i in [1,5,10,100]:
    print 'python ',i,timeit.repeat('period_analysis_py(ids,land_yx)', setup="from __main__ import period_analysis_py,ids,land_yx", repeat=3,number=1)

# prepare for test
# def period_analysis_cython(ids,lats_lons):
#     summary_=da.DimArray(axes=[ids,sorted(set([pp[0] for pp in lats_lons])),sorted(set([pp[1] for pp in lats_lons])),['cumulative_heat','hottest_day_shift']],dims=['period_id','lat','lon','type'])
#     for lat_lon in lats_lons:
#         ll=period['period_length'][ids,lat_lon[0],lat_lon[1]]
#         mm=period['period_midpoints'][ids,lat_lon[0],lat_lon[1]]-tas.time[0]
#
#         cold_ll=np.asarray(mm[ll<0],np.int)
#         cold_mm=np.asarray(ll[ll<0],np.int)
#
#         warm_ll=np.asarray(ll[ll>0],np.int)
#         warm_mm=np.asarray(mm[ll>0],np.int)
#
#         tt=np.asarray(tas[:,lat_lon[0],lat_lon[1]],np.float)
#
#         return  warm_mm,warm_ll,tt
#
# mm,ll,tt=period_analysis_cython(period.period_id,land_yx)
# np.savetxt('data/tests/mm',mm)
# np.savetxt('data/tests/ll',ll)
# np.savetxt('data/tests/tt',tt)

# def period_analysis_py_single(ll,mm,tt):
#     ho=ll.copy()*0
#     cu=np.array(ll.copy()*0,np.float)
#     for i in range(len(ll)):
#         days=range(mm[i]-int(abs(ll[i])/2.),mm[i]+int(round(abs(ll[i])/2.)))
#         cu[i]=np.nansum(tt[days])
#         ho[i]=days[np.nanargmax(tt[days])]-mm[i]
#     return cu,ho

# sys.path.append('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/persistence_in_models/')
# from cython_function import *
#
# mm=np.array(np.loadtxt('data/tests/mm'),np.int32)
# ll=np.array(np.loadtxt('data/tests/ll'),np.int32)
# tt=np.array(np.loadtxt('data/tests/tt'),np.float)
# hh=np.array(ll.copy()*0,np.int)
#
# print period_analysis(mm,ll,tt)
# print period_analysis_py(mm,ll,tt)
#
# print timeit.timeit('period_analysis(mm,ll,tt)', setup="from __main__ import period_analysis,mm,ll,tt", number=10)
# print timeit.timeit('period_analysis_py(mm,ll,tt)', setup="from __main__ import period_analysis_py,mm,ll,tt", number=10)
#
# print mm,ll
