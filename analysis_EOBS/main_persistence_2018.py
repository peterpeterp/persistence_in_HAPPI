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
raw_file='data/EOBS/All-Hist/tg_0.50deg_reg_v17.0.nc'

result=try_several_times('cdo -O mergetime '+raw_file+' '+raw_file.replace('v17.0','2018')+' '+raw_file.replace('v17.0','merged'),1,120)
merged_file = raw_file.replace('v17.0','merged')

nc =  da.read_nc(merged_file)
tas = nc['tg']
tas_time = nc['time']
time_axis=np.array([dd.year + (dd.timetuple().tm_yday-1) / 365. for dd in num2date(tas_time,units = tas_time.units)])
month=np.array([dd.month for dd in num2date(tas_time,units = tas_time.units)])

detrend_file=merged_file.replace('.nc','_detrended.nc')
result=try_several_times('cdo -O detrend '+merged_file+' '+detrend_file,1,360)

yday_clim=merged_file.replace('.nc','_clim.nc')
result=try_several_times('cdo -O ydaymean '+detrend_file+' '+yday_clim,1,120)

anom_file=merged_file.replace('.nc','_anom.nc')
result=try_several_times('cdo -O sub '+detrend_file+' '+yday_clim+' '+anom_file,1,120)

# # state
tas_state_file=merged_file.replace('.nc','_state.nc')
prsfc.temp_anomaly_to_ind(anom_file,tas_state_file,var_name='tg')

# clean
os.system('rm '+merged_file+' '+a+' '+b)


#################
# Precipitation
#################
raw_file='data/EOBS/All-Hist/rr_0.50deg_reg_v17.0.nc'
result=try_several_times('cdo -O mergetime '+raw_file+' '+raw_file.replace('v17.0','2018')+' '+raw_file.replace('v17.0','merged'),1,120)
merged_file = raw_file.replace('v17.0','merged')

pr_state_file=merged_file.replace('.nc','_state.nc')
prsfc.precip_to_index(merged_file,pr_state_file,var_name='rr',unit_multiplier=1, states={'dry':{'mod':'below','threshold':1}, 'wet':{'mod':'above','threshold':1}, '5mm':{'mod':'above','threshold':5}, '10mm':{'mod':'above','threshold':10}})



#################
# Compound State
#################
compound_state_file=pr_state_file.replace('rr_0.50','cpd_0.50')
prsfc.compound_precip_temp_index(combinations={'dry-warm':[[pr_state_file,'dry'],[tas_state_file,'warm']]} ,out_file=compound_state_file)
gc.collect()

#################
# Persistence
#################
#prsfc.get_persistence(tas_state_file,states_to_analyze=['warm'],lat_name='latitude',lon_name='longitude')
prsfc.get_persistence(pr_state_file,states_to_analyze=['10mm'],lat_name='latitude',lon_name='longitude')
prsfc.get_persistence(compound_state_file,states_to_analyze=['dry-warm'],lat_name='latitude',lon_name='longitude')
