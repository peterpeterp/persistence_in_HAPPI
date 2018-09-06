import os,sys,glob,datetime,time
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date

nc_in=Dataset('data/HadGHCND_TMean_data3D.day1-365.1950-2014.nc','r')
ID=nc_in.variables['ID'][:]
lon=nc_in.variables['lon'][:]
lat=nc_in.variables['lat'][:]
year=nc_in.variables['year'][:]
day=nc_in.variables['day'][:]
tas=nc_in.variables['tas'][:,:,:]

nc_in=Dataset('data/91_7_trend_mean_TMean.nc','r')
trend=nc_in.variables['trend'][:,:,:]

# time_axis=[]
# for yr in year:
# 	dt= datetime.datetime(year=yr, month=1, day=1)
# 	for dy in day:
# 		#print time.mktime(dt.timetuple())+86400.0*(dy-1)
# 		time_axis.append(time.mktime(dt.timetuple())+86400.0*(dy-1))

tas-=trend

time_axis=[]
for yr in year:
	for dy in day:
		time_axis.append((yr-1949)*365+dy-1)


tas_new=np.zeros([65*365,1319])*np.nan
for q in range(len(ID)):
	tas_new[:,q]=tas[:,:,q].reshape(365*65)

lon_new=np.arange(-180,183.75,3.75)
lat_new=np.arange(-90,92.5,2.5)

tas_grid=np.zeros([65*365,len(lat_new),len(lon_new)])*np.nan
for q in range(len(ID)):
	tas_grid[:,np.where(lat_new==lat[q])[0][0],np.where(lon_new==lon[q])[0][0]]=tas_new[:,q]

tas_grid[tas_grid<-100]=np.nan

nc_out=Dataset('data/HadGHCND_TMean_grided.1950-2014.nc','w')
nc_out.createDimension('time', len(time_axis))
nc_out.createDimension('lat', len(lat_new))
nc_out.createDimension('lon', len(lon_new))

outVar = nc_out.createVariable('time', 'f', ('time',)) 
outVar[:]=time_axis[:]	
outVar.setncattr('units','days since 1949-01-01 00:00:00')
outVar.setncattr('calendar','365_day')

outVar = nc_out.createVariable('lat', 'f', ('lat',))
outVar[:]=lat_new[:]
outVar.setncattr('units','deg south')
outVar = nc_out.createVariable('lon', 'f', ('lon',))
outVar[:]=lon_new[:]
outVar.setncattr('units','deg east')

outVar = nc_out.createVariable('tas', 'f', ('time','lat','lon',),fill_value='NaN')
outVar[:]=tas_grid[:,:]

nc_out.close()

