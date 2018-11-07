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

anom = tas.copy() * np.nan
for y in tas.lat:
	print(y)
	for x in tas.lon:
		tmp__ = tas[:,y,x]
		notna = np.where(np.isfinite(tmp__))[0]
		if len(notna)>365*40:
			for day in range(1,367):
				days = np.where(yday[notna] == day)[0]
				tmp = tmp__.values[notna[days]]
				m, b, r_val, p_val, std_err = stats.linregress(time_axis[notna[days]],tmp)
				tmp = tmp - (time_axis[notna[days]]*m + b)
				tmp = tmp - np.nanmean(tmp)
				anom[:,y,x].ix[notna[days]] = tmp

da.Dataset({'tas':anom,'time':nc['time'],'lat':nc['lat'],'lon':nc['lon']}).write_nc(raw_file.replace('.nc','_anom.nc'))

# # state
tas_state_file=raw_file.replace('.nc','_state.nc')
prsfc.temp_anomaly_to_ind(raw_file.replace('.nc','_anom.nc'),tas_state_file,var_name='tas')

prsfc.get_persistence(tas_state_file,states_to_analyze=['warm'],lat_name='lat',lon_name='lon')
