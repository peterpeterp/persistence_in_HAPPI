import os,sys,glob,time,collections,signal
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import subprocess as sub

sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
import __settings
model_dict=__settings.model_dict

sys.path.append('/global/homes/p/pepflei/check/weather_persistence/')
from persistence_functions import *

model=sys.argv[1]
print model

in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

try:
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
	land_mask_file='/global/homes/p/pepflei/masks/landmask_'+grid+'_NA-1.nc'
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
	working_path='data/'+model+'/'
	land_mask_file='data/'+model+'/landmask_'+grid+'_NA-1.nc'


for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2115','2106/2115','2006/2015']):
	if scenario==sys.argv[2]:
		os.system('mkdir '+working_path+scenario)
		run_list=sorted([path.split('/')[-1].split('_')[-1].split('.')[0] for path in glob.glob('/global/cscratch1/sd/pepflei/EKE/'+model+'/'+scenario+'/monEKE*')])[0:100]
		for run in run_list:

			tmp_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/day/atmos/tas/'
			raw_file=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
			tas_state_file=raw_file.replace('.nc','_state.nc')

			tas_period_file=tas_state_file.replace('_state.nc','_period_check.nc')
			print(tas_period_file)
			get_persistence(tas_state_file,tas_period_file,overwrite=True)
			gc.collect()
