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
	'pr':['dry','5mm','10mm'],
	'tas':['warm'],
	'cpd':['dry-warm'],
}

for style,states in style_dict.items():	#,'cpd','tas'
	for scenario in ['Plus15-Future']:
		state_files = sorted(glob.glob(working_path+scenario+'/'+style+'/'+style+'_*_state.nc'))
		for state_file in state_files:
			percentage_file = state_file.replace('state.nc','numberXXX.nc').replace('/'+style+'/','/stateCount/')


			# # number of valid time steps
			# result=try_several_times('cdo -O setmissval,nan ' + state_file.replace('_state.nc','.nc') + ' ' + state_file.replace('_state.nc','.nc_tmp1') ,3,60)
			# result=try_several_times('cdo -O setmissval,0 ' + state_file.replace('.nc','.nc_tmp1') + ' ' + state_file.replace('.nc','.nc_tmp2') ,3,60)
			# result=try_several_times('cdo -O yseassum -setrtoc,-9999,9999,1 ' + state_file.replace('.nc','.nc_tmp2') + ' ' + percentage_file.replace('XXX','Valid') ,3,60)
			# os.system('rm '+state_file.replace('.nc','.nc_tmp*'))

			# number of states
			for state in states:
				result=try_several_times('cdo -O yseassum -selvar,'+state+' ' + state_file + ' ' + percentage_file.replace('XXX',state) ,3,60)


		os.system('mkdir data/' + model + '/state_stats')
		for state in states:
			try_several_times('cdo -O ensmean ' + working_path+scenario+'/'+style+'_*_number'+state+'.nc ' + 'data/' + model + '/state_stats/' + style + '_' + model +'_' +scenario + '_number'+state+'.nc',3,240)
