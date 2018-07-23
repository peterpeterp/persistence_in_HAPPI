import os,sys,glob,time,collections,signal
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
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

sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
import __settings
model_dict=__settings.model_dict

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
from persistence_functions import *

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
		tmp_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/day/atmos/pr/'
		run_list=sorted([path.split('/')[-1].split('_')[-1].split('.')[0] for path in glob.glob('/global/cscratch1/sd/pepflei/EKE/'+model+'/'+scenario+'/monEKE*')])[0:100]
		print(run_list)
		for run in run_list:
			start_time=time.time()


			raw_file=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
			if len(glob.glob(working_path+scenario+'/*pr*'+run+'*'))<2:

				# get daily temp
				out_file_name_tmp=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'_tmp.nc'
				command='cdo -O mergetime '+tmp_path+run+'/* '+out_file_name_tmp
				result=try_several_times(command,2,60)
				result=try_several_times('cdo -O -selyear,'+selyears+' '+out_file_name_tmp+' '+raw_file,2,60)
				result=try_several_times('rm '+out_file_name_tmp)

				# mask ocean
				land_file=raw_file.replace('.nc','_land.nc')
				result=try_several_times('cdo -O mul '+raw_file+' '+land_mask_file+' '+land_file)

				# # state
				state_file=raw_file.replace('.nc','_state.nc')
				precip_to_index(land_file,state_file,overwrite=True,unit_multiplier=86400,threshold=1)

				# persistence
				get_persistence(state_file,raw_file.replace('.nc','_period.nc'),overwrite=True)

				if os.path.isfile(raw_file.replace('.nc','_period.nc')):
					print run,' processing time:',time.time()-start_time
				else:
					print run,' ------- fail '


				# clean
				os.system('rm '+land_file+' '+state_file+' '+raw_file)
