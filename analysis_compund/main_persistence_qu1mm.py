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
	from persistence_functions import *

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
		run_list=sorted([path.split('/')[-1].split('_')[-1].split('.')[0] for path in glob.glob('/global/cscratch1/sd/pepflei/EKE/'+model+'/All-Hist/monEKE*')])[0:100]
		for run in run_list:
			print(run)
			start_time=time.time()

			###############
			# Precipitation
			###############

			tmp_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/day/atmos/pr/'
			raw_file=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
			pr_state_file=raw_file.replace('.nc','_state_qu1mm.nc')
			if os.path.isfile(pr_state_file) == False:

				# get daily pr
				out_file_name_tmp=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'_tmp.nc'
				command='cdo -O mergetime '+tmp_path+run+'/* '+out_file_name_tmp
				result=try_several_times(command,2,60)
				result=try_several_times('cdo -O -selyear,'+selyears+' '+out_file_name_tmp+' '+raw_file,2,60)
				result=try_several_times('rm '+out_file_name_tmp)

				# mask ocean
				land_file=raw_file.replace('.nc','_land.nc')
				result=try_several_times('cdo -O mul '+raw_file+' '+land_mask_file+' '+land_file)

				# # state
				if scenario == 'All-Hist':
					prsfc.precip_to_index(land_file,pr_state_file,overwrite=True,unit_multiplier=86400,threshold=1)

				else:
					pr_percentile_file = glob.glob(working_path+'All-Hist'+'/pr_*_'+run+'_percentageState1.nc')[0]

					if os.path.isfile(pr_percentile_file):
						# import persistence_functions as prsfc; reload(prsfc)
						prsfc.precip_to_index_percentile(land_file,pr_state_file,pr_percentile_file,overwrite=True)

				# clean
				os.system('rm '+land_file)

			###############
			# Compound
			###############
			compound_state_file=pr_state_file.replace('tas_Aday','cpd_Aday')
			tas_state_file=pr_state_file.replace('pr_Aday','tas_Aday').replace('_qu1mm','')
			if os.path.isfile(compound_state_file) == False:
				prsfc.compound_precip_temp_index(tas_state_file,pr_state_file,compound_state_file)

			gc.collect()

			###############
			# Compound
			###############

			compound_period_file=compound_state_file.replace('_state_qu1mm.nc','_period_qu1mm.nc')
			print(compound_period_file)
			if os.path.isfile(compound_period_file) == False:
				prsfc.get_persistence(compound_state_file,compound_period_file,overwrite=True)
			gc.collect()
			pr_period_file=pr_state_file.replace('_state_qu1mm.nc','_period_qu1mm.nc')
			print(pr_period_file)
			if os.path.isfile(pr_period_file) == False:
				prsfc.get_persistence(pr_state_file,pr_period_file,overwrite=True)
			gc.collect()
