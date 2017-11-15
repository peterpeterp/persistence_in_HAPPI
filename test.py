import os,sys,glob,time,collections,gc,itertools
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import matplotlib.pylab as plt
import dimarray as da
from scipy.optimize import curve_fit
from lmfit import  Model
import pandas as pd

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
sys.path.append('/Users/peterpfleiderer/Documents/Projects/weather_persistence/')
from persistence_functions import *

mask=da.read_nc('data/tests/landmask_96x192_NA-1.nc')['landmask']
land_yx=[(period.lat[np.argmin(abs(lat-period.lat))],period.lon[np.argmin(abs(lon-period.lon))]) for lat,lon in itertools.product(mask.lat,mask.lon) if mask[lat,lon]==1]

period=da.read_nc('data/tests/tas_Aday_ECHAM6-3-LR_Plus20-Future_CMIP5-MMM-est1_v2-0_run010_period.nc')
tas=da.read_nc('data/tests/tas_Aday_ECHAM6-3-LR_Plus20-Future_CMIP5-MMM-est1_v2-0_run010.nc')




def period_days(per_id,lat,lon):
    ll=period['period_length'][per_id,lat,lon]
    mm=period['period_midpoints'][per_id,lat,lon]
    return np.arange(mm-int(abs(ll)/2.),mm+round(abs(ll)/2.),1)


def hottest_day_offset(per_id,lat,lon):
    days=period_days(per_id,lat,lon)
    return days[np.nanargmax(np.array(tas['tas'][days,lat,lon]).flatten())]-period['period_midpoints'][per_id,lat,lon]

def cumulative_heat(per_id,lat,lon):
    days=period_days(per_id,lat,lon)
    return np.nansum(tas['tas'][days,lat,lon])







def period_analysis(ids,lats_lons):
    summary_=da.DimArray(axes=[ids,sorted(set([pp[0] for pp in lats_lons])),sorted(set([pp[1] for pp in lats_lons])),['cumulative_heat','hottest_day_shift']],dims=['period_id','lat','lon','type'])
    for per_id,lat_lon in itertools.product(ids,lats_lons):
        ll=period['period_length'][per_id,lat_lon[0],lat_lon[1]]
        if ll>0 & period['period_season'][per_id,lat_lon[0],lat_lon[1]]==1:
            mm=period['period_midpoints'][per_id,lat_lon[0],lat_lon[1]]
            days=np.arange(mm-int(abs(ll)/2.),mm+round(abs(ll)/2.),1)
            summary_[per_id,lat_lon[0],lat_lon[1],'cumulative_heat']=np.nansum(tas['tas'][days,lat_lon[0],lat_lon[1]])
            summary_[per_id,lat_lon[0],lat_lon[1],'hottest_day_shift']=days[np.nanargmax(np.array(tas['tas'][days,lat_lon[0],lat_lon[1]]).flatten())]-mm
    return  summary_

time_0=time.time()
summary_=period_analysis(period.period_id,land_yx)
print time.time()-time_0

per_id=24
lat=period.lat[65]
lon=50.625


print 'season:',period['period_season'][per_id,lat,lon]
print 'len:',period['period_length'][per_id,lat,lon]
print 'midpoint:',period['period_midpoints'][per_id,lat,lon]
days=period_days(per_id,lat,lon)
print days
print np.array(tas['tas'][days,lat,lon]).flatten()
print np.array(tas['tas'][46620.5:46626.5,lat,lon]).flatten()

time_0=time.time()
ho=hottest_day_offset(per_id,lat,lon)
cu=cumulative_heat(per_id,lat,lon)
print time.time()-time_0
time_0=time.time()
cu,ho=period_analysis(per_id,lat,lon)
print time.time()-time_0
