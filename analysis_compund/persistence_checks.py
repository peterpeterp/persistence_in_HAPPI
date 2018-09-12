import os,sys,glob,time,collections,signal,gc
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import subprocess as sub

sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
import __settings
model_dict=__settings.model_dict

sys.path.append('/global/homes/p/pepflei/check/weather_persistence/')
from persistence_functions import *

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

model=sys.argv[1]
print model

in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

try:
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
	land_mask_file='/global/homes/p/pepflei/masks/landmask_'+grid+'_NA-1.nc'
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
	working_path='data/'+model+'/'
	land_mask_file='data/'+model+'/landmask_'+grid+'_NA-1.nc'


for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2115','2106/2115','2006/2015']):
	if scenario==sys.argv[2]:
		os.system('mkdir '+working_path+scenario)
		run_list=sorted([path.split('/')[-1].split('_')[-1].split('.')[0] for path in glob.glob('/global/cscratch1/sd/pepflei/EKE/'+model+'/'+scenario+'/monEKE*')])[0:100]
		for run in run_list:

			tmp_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/day/atmos/tas/'
			raw_file=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'

			# get daily temp
			out_file_name_tmp=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'_tmp.nc'
			command='cdo -O mergetime '+tmp_path+run+'/* '+out_file_name_tmp
			result=try_several_times(command,2,60)
			result=try_several_times('cdo -O -selyear,'+selyears+' '+out_file_name_tmp+' '+raw_file,2,60)
			result=try_several_times('rm '+out_file_name_tmp)

			# mask ocean
			land_file=raw_file.replace('.nc','_land.nc')
			result=try_several_times('cdo -O mul '+raw_file+' '+land_mask_file+' '+land_file)

			# detrend
			a=raw_file.replace('.nc','_a.nc')
			b=raw_file.replace('.nc','_b.nc')
			result=try_several_times('cdo -O trend '+land_file+' '+a+' '+b)
			detrend_1=raw_file.replace('.nc','_detrend_1.nc')
			result=try_several_times('cdo -O subtrend '+land_file+' '+a+' '+b+' '+detrend_1,1,120)

			runmean=raw_file.replace('.nc','_runmean.nc')
			result=try_several_times('cdo -O runmean,90 '+detrend_1+' '+runmean,1,120)

			detrend_cut=raw_file.replace('.nc','_detrend_cut.nc')
			command='cdo -O delete,timestep='
			for i in range(1,46,1): command+=str(i)+','
			for i in range(1,46,1): command+=str(-i)+','
			result=try_several_times(command+' '+detrend_1+' '+detrend_cut)
			anom_file=raw_file.replace('.nc','_anom.nc')
			result=try_several_times('cdo -O sub '+detrend_cut+' '+runmean+' '+anom_file,1,120)

			# # state
			state_file=raw_file.replace('.nc','_state_check.nc')
			temp_anomaly_to_ind(anom_file,state_file,overwrite=True)

			tas_period_file=tas_state_file.replace('_state_check.nc','_period_check.nc')
			print(tas_period_file)
			get_persistence(tas_state_file,tas_period_file,overwrite=True)

			asdasd

			gc.collect()
