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

try:
	os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter/')
	working_path='/p/tmp/pepflei/HAPPI/raw_data/SPI/'+model+'/'
	home_path = '/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/'
except:
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/SPI/'+model+'/'
	home_path = '/global/homes/p/pepflei/persistence_in_models/'


overwrite=True

os.system('cdo -V')
os.system('export SKIP_SAME_TIME=1')


all_files_hist=sorted(glob.glob(working_path+'All-Hist'+'/pr_Amon_*_'+'All-Hist'+'*'+'.nc'))
all_files_fut=sorted(glob.glob(working_path+'Plus20-Future'+'/pr_Amon_*_'+'Plus20-Future'+'*'+'.nc'))

bigOne = da.read_nc(working_path+'pr_big_merge_SPI3.nc')['SPI']

dummy_hist = da.read_nc(all_files_hist[0])['pr'].squeeze()
dummy_fut = da.read_nc(all_files_fut[0])['pr'].squeeze()
for file_hist,file_fut,fi in zip(all_files_hist,all_files_fut,range(len(all_files_hist))):
	print(file_hist)
	out_hist = dummy_hist.copy()*np.nan
	out_fut = dummy_fut.copy()*np.nan

	indices = np.arange(fi*11*12 ,(fi+1)*11*12 -12)
	out_hist[:,0:,:] = bigOne.ix[indices,:,:]
	out_hist.ix[:2,:,:] = np.nan
	out_fut[:,0:,:] = bigOne.ix[indices + 13200,:,:]
	out_fut.ix[:2,:,:] = np.nan

	da.Dataset({'SPI3':out_hist}).write_nc(file_hist.replace('pr','SPI3'))
	da.Dataset({'SPI3':out_fut}).write_nc(file_fut.replace('pr','SPI3'))
