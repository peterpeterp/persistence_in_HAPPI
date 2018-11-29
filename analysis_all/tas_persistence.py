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

	sys.path.append('/global/homes/p/pepflei/weather_persistence/')
	import persistence_functions as prsfc; reload(prsfc)

	print model
except:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
	model='CAM4-2degree'
	working_path='data/'+model+'/'
	chosen_scenario='All-Hist'

	sys.path.append('/Users/peterpfleiderer/Projects/Persistence/weather_persistence/')
	import persistence_functions as prsfc; reload(prsfc)

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
		run_list=model_dict['runs'][scenario]
		for run in run_list:
			print(run)
			tmp_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/day/atmos/tas/'
			# check if run exists
			if len(glob.glob(tmp_path+run+'/*'))>0:
				raw_file=working_path+scenario+'/tas/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
				tas_state_file=raw_file.replace('.nc','_state.nc')

				# get daily temp
				out_file_name_tmp=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'_tmp.nc'
				command='cdo -O mergetime '+tmp_path+run+'/* '+out_file_name_tmp
				result=try_several_times(command,2,60)
				result=try_several_times('cdo -O -selyear,'+selyears+' '+out_file_name_tmp+' '+raw_file,2,60)
				result=try_several_times('rm '+out_file_name_tmp)

				# mask ocean
				land_file=raw_file.replace('.nc','_land.nc')
				result=try_several_times('cdo -O mul '+raw_file+' '+land_mask_file+' '+land_file)

				# get ydaymean
				yday_clim=raw_file.replace('.nc','_clim.nc')
				result=try_several_times('cdo -O ydaymean '+land_file+' '+yday_clim,1,120)

		climatology_file = 'data/'+model+'/'+'tas'+'_'+model+'_'+scenario+'_dayClim.nc'
		result=try_several_times('cdo -O ensmean '+working_path+scenario+'/tas/tas_Aday*'+model+'*'+scenario+'*_clim.nc '+climatology_file,1,600)


		for run in run_list:
			print(run)
			start_time=time.time()

			###############
			# Temperature
			###############

			tmp_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/day/atmos/tas/'
			# check if run exists
			if len(glob.glob(tmp_path+run+'/*'))>0:
				raw_file=working_path+scenario+'/tas/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
				land_file=raw_file.replace('.nc','_land.nc')

				anom_file=raw_file.replace('.nc','_anom.nc')
				result=try_several_times('cdo -O sub '+land_file+' '+climatology_file+' '+anom_file,1,120)

				# # state
				tas_state_file=raw_file.replace('.nc','_state.nc')
				prsfc.temp_anomaly_to_ind(anom_file,tas_state_file)

				# clean
				os.system('rm '+raw_file)

				# ###############
				# # Persistence
				# ###############
				prsfc.get_persistence(tas_state_file,states_to_analyze=['warm'])
				gc.collect()


'''
for model in NorESM1 MIROC5 ECHAM6-3-LR CAM4-2degree; do nohup python analysis_all/tas_persistence.py $model All-Hist > out/${model}+tasHi & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done;
for model in NorESM1 MIROC5 ECHAM6-3-LR CAM4-2degree; do nohup python analysis_all/tas_persistence.py $model Plus20-Future > out/${model}+tas20 & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done;
for model in NorESM1 MIROC5 ECHAM6-3-LR CAM4-2degree; do nohup python analysis_all/tas_persistence.py $model Plus15-Future > out/${model}+tas15 & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done;
'''
#
