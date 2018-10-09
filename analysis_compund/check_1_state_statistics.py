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

os.chdir('/global/homes/p/pepflei/')
model=sys.argv[1]
working_path='/global/cscratch1/sd/pepflei/'+model+'/'
sys.path.append('/global/homes/p/pepflei/weather_persistence/')
import persistence_functions as prsfc; reload(prsfc)

sys.path.append('persistence_in_models/')
import __settings
model_dict=__settings.model_dict

for style in ['pr','cpd','tas']:
	for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2115','2106/2115','2006/2015']):
		state_files = sorted(glob.glob(working_path+scenario+'/'+style+'_*_state.nc'))
		for state_file in state_files:
			percentage_file = state_file.replace('state.nc','percentageState1.nc')
			os.system('rm '+percentage_file)
			for i in range(3):
				if os.path.isfile(percentage_file):
					if os.stat(percentage_file).st_size < 78000:
						os.system('rm '+percentage_file)
					else:
						break
				result=try_several_times('cdo yseassum -chname,state,qu -divc,36.5 -setrtoc,-1,0,0 ' + state_file + ' ' + percentage_file ,3,60)


		try_several_times('cdo ensmean ' + working_path+scenario+'/'+style+'_*_percentageState1.nc ' + 'data/' + model + '/' + style + '_' + model +'_' +scenario + '_percentageState1.nc',3,240)
