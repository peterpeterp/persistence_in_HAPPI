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
raw_file='data/EOBS/All-Hist/tg_0.50deg_reg_v17.0.nc'

result=try_several_times('cdo -O mergetime '+raw_file+' '+raw_file.replace('v17.0','2018')+' '+raw_file.replace('v17.0','merged'),1,120)
merged_file = raw_file.replace('v17.0','merged')

clean_file = merged_file.replace('.nc','_cut.nc')
try_several_times('cdo -O delete,timestep=25111/25202 '+merged_file+' '+clean_file,1,600)

nc =  da.read_nc(clean_file)
tas = nc['tg']
tas_time = nc['time']
time_axis=np.array([dd.year + (dd.timetuple().tm_yday-1) / 365. for dd in num2date(tas_time,units = tas_time.units)])
month=np.array([dd.month for dd in num2date(tas_time,units = tas_time.units)])
yday=np.array([dd.timetuple().tm_yday for dd in num2date(tas_time,units = tas_time.units)])


for day in range(1,367):
	days = np.where((yday == day))[0]
	tmp_file = clean_file.replace('.nc','.nc_'+str(day))
	da.Dataset({'tg':tas.ix[days],'latitude':nc['latitude'],'longitude':nc['longitude'],'time':nc['time'].ix[days]}).write_nc(tmp_file)
	result=try_several_times('cdo -O detrend '+tmp_file+' '+tmp_file+'_detrend',1,120)


all_files = glob.glob(clean_file.replace('.nc','.nc_*_detrend'))
try_several_times('cdo -O mergetime '+' '.join(all_files[:100])+' '+clean_file.replace('.nc','_anom_1.nc'),1,600)
try_several_times('cdo -O mergetime '+' '.join(all_files[100:200])+' '+clean_file.replace('.nc','_anom_2.nc'),1,600)
try_several_times('cdo -O mergetime '+' '.join(all_files[200:])+' '+clean_file.replace('.nc','_anom_3.nc'),1,600)
try_several_times('cdo -O mergetime '+clean_file.replace('.nc','_anom_1.nc')+' '+clean_file.replace('.nc','_anom_2.nc')+' '+clean_file.replace('.nc','_anom_3.nc')+' '+clean_file.replace('.nc','_anom.nc'),1,600)

result = try_several_times('rm '+clean_file.replace('.nc','.nc_*'),1,120)
result = try_several_times('rm '+clean_file.replace('.nc','_anom_1.nc'),1,120)
result = try_several_times('rm '+clean_file.replace('.nc','_anom_2.nc'),1,120)
result = try_several_times('rm '+clean_file.replace('.nc','_anom_3.nc'),1,120)

result = try_several_times('cdo -O ydaymean '+clean_file.replace('.nc','_anom.nc')+' '+clean_file.replace('.nc','_clim.nc'),1,120)
result = try_several_times('cdo -O sub '+clean_file.replace('.nc','_anom.nc')+' '+clean_file.replace('.nc','_clim.nc')+' '+clean_file.replace('.nc','_anom_detrend.nc'),1,120)
#
#
# time_ = time.time()
# anom = tas.copy() * np.nan
# for y in tas.latitude:
# 	print(y, time.time() - time_);	time_ = time.time()
# 	for x in tas.longitude:
# 		for day in range(1,367):
# 			days = np.where(yday == day)[0]
# 			tmp = tas[days,y,x].values
# 			notna = np.where(np.isfinite(tmp))[0]
# 			if len(notna)>1:
# 				tmp = tmp[notna]
# 				m, b, r_val, p_val, std_err = stats.linregress(time_axis[days[notna]],tmp)
# 				tmp -= (m*time_axis[days[notna]] + b)
# 				tmp -= np.nanmean(tmp)
# 				anom[:,y,x].ix[days[notna]] = tmp
#
# #anom__ = da.DimArray(anom.values, axes=tas.axes, dims=tas.dims)
# da.Dataset({'tg':anom,'latitude':nc['latitude'],'longitude':nc['longitude'],'time':nc['time']}).write_nc(merged_file.replace('.nc','_anom.nc'))
#



# # state
tas_state_file=clean_file.replace('.nc','_state.nc')
prsfc.temp_anomaly_to_ind(clean_file.replace('.nc','_anom_detrend.nc'),tas_state_file,var_name='tg')

#################
# Precipitation
#################
raw_file='data/EOBS/All-Hist/rr_0.50deg_reg_v17.0.nc'
#result=try_several_times('cdo -O mergetime '+raw_file+' '+raw_file.replace('v17.0','2018')+' '+raw_file.replace('v17.0','merged'),1,120)
merged_file = raw_file.replace('v17.0','merged')

pr_state_file=merged_file.replace('.nc','_state.nc')
#prsfc.precip_to_index(merged_file,pr_state_file,var_name='rr',unit_multiplier=1, states={'dry':{'mod':'below','threshold':1}, 'wet':{'mod':'above','threshold':1}, '5mm':{'mod':'above','threshold':5}, '10mm':{'mod':'above','threshold':10}})



#################
# Compound State
#################
compound_state_file=pr_state_file.replace('rr_0.50','cpd_0.50')
prsfc.compound_precip_temp_index(combinations={'dry-warm':[[pr_state_file,'dry'],[tas_state_file,'warm']]} ,out_file=compound_state_file)
gc.collect()

#################
# Persistence
#################
prsfc.get_persistence(tas_state_file,states_to_analyze=['warm'],lat_name='latitude',lon_name='longitude')
#prsfc.get_persistence(pr_state_file,states_to_analyze=['dry','10mm','5mm'],lat_name='latitude',lon_name='longitude')
prsfc.get_persistence(compound_state_file,states_to_analyze=['dry-warm'],lat_name='latitude',lon_name='longitude')
