import os,sys,glob,time,collections,gc
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
sys.path.append('/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/')
import __settings
model_dict=__settings.model_dict

try:
	model=sys.argv[1]
	print model

except:
	model = 'CAM4-2degree'


working_path='/global/cscratch1/sd/pepflei/SPI/'+model+'/'
working_path='/p/tmp/pepflei/HAPPI/raw_data/SPI_stuff/'+model+'/'


overwrite=True

os.system('cdo -V')
os.system('export SKIP_SAME_TIME=1')

try_several_times('Rscript analysis_spi/SPI.r '+working_path+'pr_big_merge.nc pr 3 -13200 -13200 -1 '+working_path+'pr_big_merge_SPI3.nc',1,900000)
