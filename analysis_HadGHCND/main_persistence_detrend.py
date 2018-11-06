import os,sys,glob,time,collections,signal,gc
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import subprocess as sub
import scipy
from scipy import signal
from scipy import stats


def wait_timeout(proc, seconds):
	"""Wait for a process to finish, or raise exception after timeout"""
	start = time.time()
	end = start + seconds
	interval = min(seconds / 1000.0, .25)

	while True:
		result = proc.poll()
		if result is not None:
			return result
		if time.time() >= end:
			os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
			return 'failed'
		time.sleep(interval)


def try_several_times(command,trials=2,seconds=60):
	for trial in range(trials):
		proc=sub.Popen(command,stdout=sub.PIPE,shell=True, preexec_fn=os.setsid)
		result=wait_timeout(proc,seconds)
		if result!='failed':
			break
	return(result)


try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/p/projects/tumble/carls/shared_folder/Persistence/')

sys.path.append('weather_persistence/')
import persistence_functions as prsfc; reload(prsfc)

start_time=time.time()

#################
# temperature
#################
raw_file='data/HadGHCND/All-Hist/HadGHCND_TMean_grided.1950-2014.nc'

nc =  da.read_nc(raw_file)
tas = nc['tas']
tas_time = nc['time']

time_axis=np.array([dd.year + (dd.timetuple().tm_yday-1) / 365. for dd in num2date(tas_time.values,units = tas_time.units)])
month=np.array([dd.month for dd in num2date(tas_time.values,units = tas_time.units)])
yday=np.array([dd.timetuple().tm_yday for dd in num2date(tas_time.values,units = tas_time.units)])


for day in range(1,367):
	days = np.where((yday == day))[0]
	tmp_file = raw_file.replace('.nc','.nc_'+str(day))
	da.Dataset({'tg':tas.ix[days],'lat':nc['lat'],'lon':nc['lon'],'time':nc['time'].ix[days]}).write_nc(tmp_file)
	result=try_several_times('cdo -O detrend '+tmp_file+' '+tmp_file+'_detrend',1,120)


all_files = glob.glob(raw_file.replace('.nc','.nc_*_detrend'))
try_several_times('cdo -O mergetime '+' '.join(all_files[:100])+' '+raw_file.replace('.nc','_anom_1.nc'),1,600)
try_several_times('cdo -O mergetime '+' '.join(all_files[100:200])+' '+raw_file.replace('.nc','_anom_2.nc'),1,600)
try_several_times('cdo -O mergetime '+' '.join(all_files[200:])+' '+raw_file.replace('.nc','_anom_3.nc'),1,600)
try_several_times('cdo -O mergetime '+raw_file.replace('.nc','_anom_1.nc')+' '+raw_file.replace('.nc','_anom_2.nc')+' '+raw_file.replace('.nc','_anom_3.nc')+' '+raw_file.replace('.nc','_anom.nc'),1,600)

result = try_several_times('rm '+raw_file.replace('.nc','.nc_*'),1,120)
result = try_several_times('rm '+raw_file.replace('.nc','_anom_1.nc'),1,120)
result = try_several_times('rm '+raw_file.replace('.nc','_anom_2.nc'),1,120)
result = try_several_times('rm '+raw_file.replace('.nc','_anom_3.nc'),1,120)

result = try_several_times('cdo -O ydaymean '+raw_file.replace('.nc','_anom.nc')+' '+raw_file.replace('.nc','_clim.nc'),1,120)
result = try_several_times('cdo -O sub '+raw_file.replace('.nc','_anom.nc')+' '+raw_file.replace('.nc','_clim.nc')+' '+raw_file.replace('.nc','_anom_detrend.nc'),1,120)

# # state
tas_state_file=raw_file.replace('.nc','_state.nc')
prsfc.temp_anomaly_to_ind(raw_file.replace('.nc','_anom_detrend.nc'),tas_state_file,var_name='tg')

prsfc.get_persistence(tas_state_file,states_to_analyze=['warm'],lat_name='lat',lon_name='lon')
