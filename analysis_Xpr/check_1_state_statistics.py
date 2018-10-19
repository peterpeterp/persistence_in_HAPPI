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

for scenario in ['All-Hist','Plus20-Future','Plus15-Future']:
	state_files = sorted(glob.glob(working_path+scenario+'/'+'pr'+'/'+'pr'+'_*_state10mm.nc'))
	for state_file in state_files:
		percentage_file = state_file.replace('state.nc','numberState1.nc').replace('/pr/','/stateCount/')
		#os.system('rm '+percentage_file)

		if os.path.isfile(percentage_file.replace('State1','Days')) == False:
			result=try_several_times('cdo -O chname,state,qu ' + state_file + ' ' + state_file.replace('.nc','.nc_tmp1') ,3,60)
			result=try_several_times('cdo -O setmissval,nan ' + state_file.replace('.nc','.nc_tmp1') + ' ' + state_file.replace('.nc','.nc_tmp2') ,3,60)
			result=try_several_times('cdo -O setmissval,0 ' + state_file.replace('.nc','.nc_tmp2') + ' ' + state_file.replace('.nc','.nc_tmp3') ,3,60)
			result=try_several_times('cdo -O yseassum -setrtoc,-100,0,0 ' + state_file.replace('.nc','.nc_tmp3') + ' ' + percentage_file ,3,60)
			result=try_several_times('cdo -O setrtoc,-100,-0.1,1 ' + state_file.replace('.nc','.nc_tmp3') + ' ' + state_file.replace('.nc','.nc_tmp4') ,3,60)
			result=try_several_times('cdo -O yseassum -setrtoc,0.1,100,1 ' + state_file.replace('.nc','.nc_tmp4') + ' ' + percentage_file.replace('State1','Days') ,3,60)

			os.system('rm '+state_file.replace('.nc','.nc_tmp*'))

	os.system('mkdir data/' + model + '/state_stats')
	try_several_times('cdo -O ensmean ' + working_path+scenario+'/stateCount/'+'pr'+'_*_numberState1.nc ' + 'data/' + model + '/state_stats/' + 'pr' + '_' + model +'_' +scenario + '_numberState1.nc',3,240)
	try_several_times('cdo -O ensmean ' + working_path+scenario+'/stateCount/'+'pr'+'_*_numberDays.nc ' + 'data/' + model + '/state_stats/' + 'pr' + '_' + model +'_' +scenario + '_numberDays.nc',3,240)
