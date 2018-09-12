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
	os.chdir('/global/homes/p/pepflei/')
	model=sys.argv[1]
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
	chosen_scenario=sys.argv[2]
	print model
except:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
	model='CAM4-2degree'
	working_path='data/'+model+'/'
	chosen_scenario='All-Hist'

sys.path.append('persistence_in_models/')
import __settings
model_dict=__settings.model_dict


in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

try:
	os.chdir('/global/homes/p/pepflei/')
	land_mask_file='/global/homes/p/pepflei/masks/landmask_'+grid+'_NA-1.nc'
except:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
	land_mask_file='data/'+model+'/landmask_'+grid+'_NA-1.nc'



for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2115','2106/2115','2006/2015']):
	if scenario==chosen_scenario:
		os.system('mkdir '+working_path+scenario)
		run_list=['ens0000']
		for run in run_list:

			raw_file=working_path+scenario+'/'+'tas_Aday_CAM4-2degree_All-Hist_est1_v1-0_ens0000.nc'

			# # mask ocean
			# land_file=raw_file.replace('.nc','_land.nc')
			# result=try_several_times('cdo -O mul '+raw_file+' '+land_mask_file+' '+land_file)
			#
			# # detrend
			# a=raw_file.replace('.nc','_a.nc')
			# b=raw_file.replace('.nc','_b.nc')
			# result=try_several_times('cdo -O trend '+land_file+' '+a+' '+b)
			# detrend_1=raw_file.replace('.nc','_detrend_1.nc')
			# result=try_several_times('cdo -O subtrend '+land_file+' '+a+' '+b+' '+detrend_1,1,120)
			#
			# runmean=raw_file.replace('.nc','_runmean.nc')
			# result=try_several_times('cdo -O runmean,90 '+detrend_1+' '+runmean,1,120)
			#
			# detrend_cut=raw_file.replace('.nc','_detrend_cut.nc')
			# command='cdo -O delete,timestep='
			# for i in range(1,46,1): command+=str(i)+','
			# for i in range(1,46,1): command+=str(-i)+','
			# result=try_several_times(command+' '+detrend_1+' '+detrend_cut)
			anom_file=raw_file.replace('.nc','_anom.nc')
			# result=try_several_times('cdo -O sub '+detrend_cut+' '+runmean+' '+anom_file,1,120)
			# os.system('rm '+land_file+' '+a+' '+b+' '+detrend_1+' '+runmean)

			sys.path.append('weather_persistence/')
			import persistence_functions as prsfc; reload(prsfc)

			# # state
			tas_state_file=raw_file.replace('.nc','_state.nc')
			prsfc.temp_anomaly_to_ind(anom_file,tas_state_file,overwrite=True)

			asdasd

			# tas_period_file=tas_state_file.replace('_state.nc','_period.nc')
			# print(tas_period_file)
			# prsfc.get_persistence(tas_state_file,tas_period_file,overwrite=True)
			#
			# # mask ocean
			# land_file=raw_file.replace('.nc','_land.nc')
			# result=try_several_times('cdo -O mul '+raw_file+' '+land_mask_file+' '+land_file)
			#
			# # detrend
			# a=raw_file.replace('.nc','_a.nc')
			# b=raw_file.replace('.nc','_b.nc')
			# result=try_several_times('cdo -O trend '+land_file+' '+a+' '+b)
			# detrend_1=raw_file.replace('.nc','_detrend_1.nc')
			# result=try_several_times('cdo -O subtrend '+land_file+' '+a+' '+b+' '+detrend_1,1,120)
			#
			# runmean=raw_file.replace('.nc','_runmean.nc')
			# result=try_several_times('cdo -O runmean,90 '+detrend_1+' '+runmean,1,120)
			#
			# detrend_cut=raw_file.replace('.nc','_detrend_cut.nc')
			# command='cdo -O delete,timestep='
			# for i in range(1,46,1): command+=str(i)+','
			# for i in range(1,46,1): command+=str(-i)+','
			# result=try_several_times(command+' '+detrend_1+' '+detrend_cut)
			anom_file=raw_file.replace('.nc','_anom_check.nc')
			# result=try_several_times('cdo -O sub '+detrend_cut+' '+runmean+' '+anom_file,1,120)
			# os.system('rm '+land_file+' '+a+' '+b+' '+detrend_1+' '+runmean+' ')
			#
			sys.path.append('check/weather_persistence/')
			import persistence_functions as prsfc; reload(prsfc)

			# # state
			tas_state_file=raw_file.replace('.nc','_state_check.nc')
			prsfc.temp_anomaly_to_ind(anom_file,tas_state_file,overwrite=True)

			# tas_period_file=tas_state_file.replace('_state_check.nc','_period_check.nc')
			# print(tas_period_file)
			# prsfc.get_persistence(tas_state_file,tas_period_file,overwrite=True)

			asdasd

			gc.collect()
