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
		run_list=model_dict[model]['runs'][scenario]
		for run in run_list:
			print(run)
			go = True
			start_time=time.time()

			###############
			# Compound
			###############
			tas_state_files=glob.glob(working_path+scenario+'/tas/tas_Aday_*'+run+'*_state.nc')
			if len(tas_state_files)==1:
				tas_state_file = tas_state_files[0]
			else:
				go = False

			pr_state_files=glob.glob(working_path+scenario+'/pr/pr_Aday_*'+run+'*_state.nc')
			if len(pr_state_files)==1:
				pr_state_file = pr_state_files[0]
			else:
				go = False

			compound_state_file=tas_state_file.replace('tas/tas_Aday','cpd/cpd_Aday')
			if os.path.isfile(compound_state_file):
				go = False

			if go:
				prsfc.compound_precip_temp_index(combinations={'dry-warm':[[pr_state_file,'dry'],[tas_state_file,'warm']]} ,out_file=compound_state_file)
				if os.path.isfile(compound_state_file.replace('state','period_dry-warm')) == False or True:
					prsfc.get_persistence(compound_state_file,states_to_analyze=['dry-warm'])
				gc.collect()




'''
for model in NorESM1 MIROC5 ECHAM6-3-LR CAM4-2degree; do nohup python analysis_all/cpd_persistence.py $model All-Hist > out/${model}+cpdHi & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done;
for model in NorESM1 MIROC5 ECHAM6-3-LR CAM4-2degree; do nohup python analysis_all/cpd_persistence.py $model Plus20-Future > out/${model}+cpd20 & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done;
for model in NorESM1 MIROC5 ECHAM6-3-LR CAM4-2degree; do nohup python analysis_all/cpd_persistence.py $model Plus15-Future > out/${model}+cpd15 & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done;
'''









#
