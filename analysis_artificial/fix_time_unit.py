import os,sys,glob,time,collections,gc,random
import numpy as np
from netCDF4 import Dataset,num2date
import dimarray as da
import subprocess as sub


try:
	model=sys.argv[1]
except:
	model = 'ECHAM6-3-LR'

scenario = 'Plus20-Future'
seed = 'v1'

print(model,scenario,seed)

try:
	sys.path.append('/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/')
	os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter/')
	in_path='/p/tmp/pepflei/HAPPI/raw_data/'+model+'/'
	out_path='/p/tmp/pepflei/HAPPI/raw_data/reg_merge/'+model+'/'
	home_path = '/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/'

except:
	sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
	os.chdir('/global/homes/p/pepflei/')


os.system('mkdir '+in_path+scenario.replace('Future','Artificial-'+str(seed)))
os.system('mkdir '+in_path+scenario.replace('Future','Artificial-'+str(seed))+'/pr/')

import __settings
model_dict=__settings.model_dict
landmask = da.read_nc('masks/landmask_'+model_dict[model]['grid']+'.nc')['landmask']

state_count_fut = da.read_nc('/p/projects/ikiimp/HAPPI/HAPPI_Peter/data/'+model+'/state_stats/pr_*'+scenario+'*')
state_count_hist = da.read_nc('/p/projects/ikiimp/HAPPI/HAPPI_Peter/data/'+model+'/state_stats/pr_*All-Hist*')

hist_files=sorted(glob.glob(in_path+'All-Hist/pr/*_All-Hist*state.nc'))

nc = Dataset(hist_files[0])
lat = nc.variables['lat'][:]
lat_nh = lat[lat>0]

for i_run,file_name in enumerate(hist_files):
	dataset = Dataset(file_name.replace('All-Hist',scenario.replace('Future','Artificial-'+str(seed))), 'a', format='NETCDF4_CLASSIC')

	dataset.variables['time'].units = nc.variables['time'].units
	dataset.variables['time'].calendar = nc.variables['time'].calendar
	dataset.close()

	
