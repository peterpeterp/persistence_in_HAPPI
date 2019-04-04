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


all_files=sorted(glob.glob(in_path+'Plus20-Artificial-'+seed+'/pr/*_Plus20-Artificial-'+seed+'*state.nc'))

for file_name in all_files:
	prsfc.get_persistence(file_name,states_to_analyze=['dry','5mm'])
