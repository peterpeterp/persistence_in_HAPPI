import os,sys,glob,time,collections,signal,gc
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import subprocess as sub

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

if os.path.isfile(raw_file.replace('.nc','_anom.nc'))==False:
	nc=da.read_nc(raw_file)
	tas=nc['tg']
	tas_time=nc['time']

	datevar=num2date(tas_time,units = tas_time.units)
	time_axis=np.array([dd.year + (dd.timetuple().tm_yday-1) / 365. for dd in datevar])
	#tas.time=time_axis

	# feb29_id = [id for id,dd in zip(range(len(time_axis)),datevar) if dd.month==2 and dd.day==29]
	# no_feb29d_id = [id for id in range(len(time_axis)) if id not in feb29_id]
	# tas=tas.ix[no_feb29d_id,:,:]

	window=tas.time.copy()
	window[:]=False
	for i in range(7):
		window[(365*i):(365*i)+91]=True

	first_possible_time_step=np.where(window==1)[0][-1] / 2

	trend=tas.copy()*np.nan
	print('detecting\n10------50-------100')
	for i,progress in zip(range(first_possible_time_step,365*68-first_possible_time_step), np.array([['-']+['']*(len(range(365*4,365*62))/20+1)]*20).flatten()[0:len(range(365*4,365*62))]):
		sys.stdout.write(progress); sys.stdout.flush()
		trend.ix[i,:,:]=np.nanmean(tas.ix[np.where(window)[0],:,:],axis=0)
		window=np.roll(window,1)

	da.Dataset({'tas_trend_91_7':trend}).write_nc(raw_file.replace('.nc','_trend.nc'))

	anom=tas.copy()-trend.copy()
	da.Dataset({'tas_anom':anom}).write_nc(raw_file.replace('.nc','_anom.nc'))

else:
	anom=da.read_nc(raw_file.replace('.nc','_anom.nc'))['tas_anom']


# state
tas_state_file=raw_file.replace('.nc','_state.nc')
prsfc.temp_anomaly_to_ind(raw_file.replace('.nc','_anom.nc'),tas_state_file,var_name='tas_anom')

#################
# Precipitation
#################
raw_file='data/EOBS/All-Hist/rr_0.50deg_reg_v17.0.nc'

pr_state_file=raw_file.replace('.nc','_state.nc')
prsfc.precip_to_index(raw_file,pr_state_file,var_name='rr',unit_multiplier=1, states={'dry':{'mod':'below','threshold':1}, 'wet':{'mod':'above','threshold':1}, '5mm':{'mod':'above','threshold':5}, '10mm':{'mod':'above','threshold':10}})



#################
# Compound State
#################
compound_state_file=pr_state_file.replace('rr_0.50','cpd_0.50')
prsfc.compound_precip_temp_index(combinations={'dry-warm':[[pr_state_file,'dry'],[tas_state_file,'warm']]} ,out_file=compound_state_file)
gc.collect()

#################
# Persistence
#################
prsfc.get_persistence(tas_state_file,states_to_analyze=['warm','cold'],lat_name='latitude',lon_name='longitude')
prsfc.get_persistence(pr_state_file,states_to_analyze=['dry','wet','5mm','10mm'],lat_name='latitude',lon_name='longitude')
prsfc.get_persistence(compound_state_file,states_to_analyze=['dry-warm'],lat_name='latitude',lon_name='longitude')
