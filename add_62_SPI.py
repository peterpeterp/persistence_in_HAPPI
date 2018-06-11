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


def try_several_times(command,trials=1,seconds=60):
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

working_path='/global/cscratch1/sd/pepflei/SPI/'+model+'/'
in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

overwrite=True

os.system('cdo -V')

for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2115','2106/2115','2006/2015']):
	os.system('export SKIP_SAME_TIME=1')
	if os.path.isdir(working_path+scenario)==False: os.system('mkdir '+working_path+scenario)
	model_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/'
	run_list=sorted([path.split('/')[-1] for path in glob.glob(model_path+'day/atmos/tasmax/*')])[0:100]
	for run in run_list:

		# precipitation monthly
		pr_file_name=working_path+scenario+'/'+glob.glob(model_path+'mon/atmos/pr/'+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
		if os.path.isfile(pr_file_name)==False or overwrite:
			run_files=glob.glob(model_path+'mon/atmos/pr/'+run+'/*')
			if len(run_files)>1:
				command='cdo -O mergetime '
				for subfile in run_files:
					command+='-selyear,'+selyears+' '+subfile+' '
				result=try_several_times(command+' '+pr_file_name)
			else:
				result=try_several_times('cdo -O selyear,'+selyears+' '+run_files[0]+' '+pr_file_name)

			result=try_several_times('Rscript '+pr_file_name+' pr 3 '+selyears.split('/')[0]+' '+selyears.split('/')[0]+' '+selyears.split('/')[1]+' SPI_'+model+'_'+scenario+'_'+run+'.nc',1,600)
