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
		run_list=[model_dict[model]['run_name']+str(i).zfill(3) for i in range(101)]
		for run in run_list:
			print(run)
			start_time=time.time()

			###############
			# Precipitation
			###############

			tmp_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/day/atmos/pr/'
			if len(glob.glob(tmp_path+run+'/*'))>0:
				raw_file=working_path+scenario+'/pr/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
				pr_state_file=raw_file.replace('.nc','_state.nc')
				if os.path.isfile(pr_state_file):
					nc = da.read_nc(pr_state_file)
					if 'state' in nc.keys():
						os.system('rm '+pr_state_file)

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

					prsfc.precip_to_index(land_file,pr_state_file,unit_multiplier=86400, states={'dry':{'mod':'below','threshold':1}, 'wet':{'mod':'above','threshold':1}, '5mm':{'mod':'above','threshold':5}, '10mm':{'mod':'above','threshold':10}})

					# clean
					os.system('rm '+land_file+' '+raw_file)

				###############
				# Persistence
				###############

				if os.path.isfile(pr_state_file.replace('state','period_dry')) == False:
					prsfc.get_persistence(pr_state_file,states_to_analyze=['dry','wet','5mm','10mm'])
				gc.collect()




#
