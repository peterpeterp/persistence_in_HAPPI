import os,sys,glob,time,collections,signal,gc
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import subprocess as sub
import scipy
from scipy import signal


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

detrend_file=raw_file.replace('.nc','_detrended.nc')
result=try_several_times('cdo -O detrend '+raw_file+' '+detrend_file,1,360)

yday_clim=raw_file.replace('.nc','_clim.nc')
result=try_several_times('cdo -O ydaymean '+detrend_file+' '+yday_clim,1,120)

anom_file=raw_file.replace('.nc','_anom.nc')
result=try_several_times('cdo -O sub '+detrend_file+' '+yday_clim+' '+anom_file,1,120)

# # state
tas_state_file=raw_file.replace('.nc','_state.nc')
prsfc.temp_anomaly_to_ind(anom_file,tas_state_file,var_name='tas')

#################
# Persistence
#################
prsfc.get_persistence(tas_state_file,states_to_analyze=['warm'],lat_name='lat',lon_name='lon')
