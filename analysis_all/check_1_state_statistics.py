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

style_dict = {
	'pr':{'states':['dry','5mm','10mm'],'days':3650},
	'tas':{'states':['warm'],'days':3560},
	'cpd':{'states':['dry-warm'],'days':3560},
}

for style,info in style_dict.items():	#,'cpd','tas'
	for scenario in ['Plus15-Future']:
		state_files = sorted(glob.glob(working_path+scenario+'/'+style+'/'+style+'_*_state.nc'))
		for state_file in state_files:

			states = info['states']
			data = da.read_nc(state_file)

			if 'stateCount' not in globals():
				stateCount = da.Dataset({})
				for state in states:
					stateCount[state] = da.DimArray(np.zeros([len(data.lat),len(data.lon)]), axes=[data.lat,data.lon],dims=['lat','lon'])
					stateCount[state].days = 0

			# number of states
			for state in states:
				stateCount[state].values += np.nansum(data[state],axis=0)
				stateCount[state].days += info['days']

		stateCount.write_nc('data/' + model + '/state_stats/' + style + '_' + model +'_' +scenario + '_stateCount.nc')
