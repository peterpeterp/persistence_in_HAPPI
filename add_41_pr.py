import os,sys,glob,time,collections
import numpy as np
from netCDF4 import Dataset,num2date
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


def try_several_times(command,trials,seconds):
	for trial in range(trials):
		proc=sub.Popen(command,stdout=sub.PIPE,shell=True, preexec_fn=os.setsid)
		result=wait_timeout(proc,seconds)
		if result!='failed':
			break
	return(result)

sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
import __settings
model_dict=__settings.model_dict

model=sys.argv[1]
print model

working_path='/global/cscratch1/sd/pepflei/TXx_pr_cor/'+model+'/'
in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

overwrite=True

os.system('cdo -V')

for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2115','2106/2115','2006/2015']):
	os.system('export SKIP_SAME_TIME=1')
	if os.path.isdir(working_path+scenario)==False: os.system('mkdir '+working_path+scenario)
	model_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/mon/atmos/pr/'
	result=try_several_times('cdo -O -ymonmean -selyear,'+selyears+' -ensmean -cat "'+model_path+'/*/*" pr_'+model+'_'+scenario+'_monClim.nc',5,600)
