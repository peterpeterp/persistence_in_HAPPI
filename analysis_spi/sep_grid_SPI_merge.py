from __future__ import print_function
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

try:
	model=sys.argv[1]
	print model

except:
	model = 'CAM4-2degree'


working_path='/global/cscratch1/sd/pepflei/SPI/'+model+'/'
in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

overwrite=True

all_files_hist=sorted(glob.glob(working_path+'All-Hist'+'/pr_Amon_*_'+'All-Hist'+'*'+'.nc'))
all_files_fut=sorted(glob.glob(working_path+'Plus20-Future'+'/pr_Amon_*_'+'Plus20-Future'+'*'+'.nc'))

dummy = da.read_nc(all_files_hist[0])['pr'].squeeze()
lat,lon = dummy.lat,dummy.lon

land_mask=da.read_nc('/global/homes/p/pepflei/masks/landmask_'+grid+'_NA-1.nc')['landmask']

print('----------- saving stuff')
for file_hist,file_fut,fi in zip(all_files_hist,all_files_fut,range(len(all_files_hist))):
	print(file)
	out_hist = dummy.copy()*np.nan
	out_fut = dummy.copy()*np.nan
	for iy,y in enumerate(lat):
		print(iy,"/",len(lat), "\r", end="")
		for ix,x in enumerate(lon):
			grid_file_name = working_path+'grid_level/'+str(y)+'_'+str(x)+'_SPI3.txt'
			if land_mask[y,x] != 1 and y>=0 and os.path.isfile(grid_file_name):
				csv = open(grid_file_name,'r').read()
				tmp_spi = np.array([])
				for dd in csv.split(';'):
					if dd == 'NA':
						tmp_spi = np.append(tmp_spi,np.nan)
					else:
						tmp_spi = np.append(tmp_spi,np.float(dd.replace('"','')))

				indices = np.arange(fi*11*12+2 ,(fi+1)*11*12 -12)
				out_hist.ix[2:,iy,ix] = tmp_spi[indices]
				out_fut.ix[2:,iy,ix] = tmp_spi[indices + 13200]

	da.Dataset({'SPI3':out_hist}).write_nc(file_hist.replace('pr','SPI3'))
	da.Dataset({'SPI3':out_fut}).write_nc(file_fut.replace('pr','SPI3'))


'''
for model in CAM4-2degree ECHAM6-3-LR MIROC5 NorESM1; do nohup python analysis_add/add_62_SPI_merged.py $model > out/$model+spi & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done;

for model in CAM4-2degree ECHAM6-3-LR MIROC5 NorESM1; do for scenario in Plus20-Future; do nohup python analysis_add/add_62_SPI.py $model $scenario > out/$model+add+$scenario & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done; done;


for model in CAM4-2degree ECHAM6-3-LR MIROC5 NorESM1; do for scenario in All-Hist Plus20-Future; do nohup cdo -ymonmean -ensmean -cat "/global/cscratch1/sd/pepflei/SPI/${model}/${scenario}/SPI*" /global/homes/p/pepflei/data/SPI/SPI_${model}_${scenario}_monClim.nc > out/$model+add & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done; done;


'''
