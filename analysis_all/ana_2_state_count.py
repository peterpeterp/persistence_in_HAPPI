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
	'tas':{'states':['warm'],'days':3650},
	'cpd':{'states':['dry-warm'],'days':3650},
}

seasons={'MAM':[3,4,5],'JJA':[6,7,8],'SON':[9,10,11],'DJF':[12,1,2]}

for style,info in style_dict.items():	#,'cpd','tas'
	for scenario in ['Plus20-Future','Plus15-Future','All-Hist']:
		state_files = sorted(glob.glob(working_path+scenario+'/'+style+'/'+style+'_*_state.nc'))
		for state_file in state_files:
			print(state_file)

			states = info['states']
			nc = da.read_nc(state_file)

			if 'calendar' in nc['time'].attrs.keys():
				datevar=num2date(nc['time'].values,units = nc['time'].units, calendar = nc['time'].calendar)
			else:
				datevar=num2date(nc['time'].values,units = nc['time'].units)
			month=np.array([date.month for date in datevar])

			if 'stateCount' not in globals():
				stateCount = da.Dataset({})
				for state in states:
					stateCount[state] = da.DimArray(np.zeros([4,len(nc.lat),len(nc.lon)]), axes=[seasons.keys(),nc.lat,nc.lon],dims=['season','lat','lon'])
					stateCount[state+'_possible_days'] = da.DimArray(np.zeros([4,len(nc.lat),len(nc.lon)]), axes=[seasons.keys(),nc.lat,nc.lon],dims=['season','lat','lon'])

			# number of states
			for state in states:
				for season in seasons.keys():
					days_in_season=np.where( (month==seasons[season][0]) | (month==seasons[season][1]) | (month==seasons[season][2]) )[0]
					stateCount[state][season].values += np.nansum(nc[state].ix[days_in_season,:,:],axis=0)
					stateCount[state+'_possible_days'][season].values += len(days_in_season)

		stateCount.write_nc('data/' + model + '/state_stats/' + style + '_' + model +'_' +scenario + '_stateCount.nc')
		del stateCount
