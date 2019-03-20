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
	working_path='/p/tmp/pepflei/HAPPI/raw_data/SPI_stuff/'+model+'/'
	home_path = '/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/'
except:
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/SPI/'+model+'/'
	home_path = '/global/homes/p/pepflei/persistence_in_models/'


overwrite=True

os.system('cdo -V')
os.system('export SKIP_SAME_TIME=1')

grid=model_dict[model]['grid']

all_files_hist=sorted(glob.glob(working_path+'All-Hist'+'/pr_Amon_*_'+'All-Hist'+'*'+'.nc'))
all_files_fut=sorted(glob.glob(working_path+'Plus20-Future'+'/pr_Amon_*_'+'Plus20-Future'+'*'+'.nc'))

dummy = da.read_nc(all_files_hist[0])['pr'].squeeze()[:,0:,:]

big_merge_hist = dummy
big_merge_fut = dummy
land_mask=da.read_nc('masks/landmask_'+grid+'_NA-1.nc')['landmask'][0:,:]

empty_year = dummy.values[:12,:,:].copy() * np.nan
big_merge_hist = np.concatenate((big_merge_hist, empty_year))
big_merge_fut = np.concatenate((big_merge_fut, empty_year))

empti_spi = da.Dataset({'SPI3':dummy.copy() * np.nan})

for file_hist,file_fut in zip(all_files_hist[1:],all_files_fut[1:]):
	print(file_hist,file_fut)
	big_merge_hist = np.concatenate((big_merge_hist, da.read_nc(file_hist)['pr'].squeeze()[:,0:,:]))
	big_merge_hist = np.concatenate((big_merge_hist, empty_year))
	big_merge_fut = np.concatenate((big_merge_fut, da.read_nc(file_fut)['pr'].squeeze()[:,0:,:]))
	big_merge_fut = np.concatenate((big_merge_fut, empty_year))

if big_merge_hist.shape[0] != 13200 or big_merge_fut.shape[0] != 13200:
	asdas

constructed_time_axis = np.append(np.arange(-132*100,0), np.arange(132*100))
oneBig = np.concatenate((big_merge_hist,big_merge_fut)) * land_mask.values
da.Dataset({'pr':da.DimArray(oneBig, axes=[constructed_time_axis,dummy.lat,dummy.lon], dims=['time','lat','lon'])}).write_nc(working_path+'pr_big_merge.nc')

del big_merge_hist, big_merge_fut, oneBig
gc.collect()

print('Rscript '+home_path+'analysis_spi/SPI.r '+working_path+'pr_big_merge.nc pr 3 -13200 -13200 -1 '+working_path+'pr_big_merge_SPI3.nc')



'''

for model in NorESM1 MIROC5 ECHAM6-3-LR CAM4-2degree; do sbatch job_Rscript.sh /p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/analysis_spi/SPI.r /p/tmp/pepflei/HAPPI/raw_data/SPI_stuff/${model}/pr_big_merge.nc pr 3 -13200 -13200 -1 /p/tmp/pepflei/HAPPI/raw_data/SPI_stuff/${model}/pr_big_merge_SPI3.nc; done;

'''
