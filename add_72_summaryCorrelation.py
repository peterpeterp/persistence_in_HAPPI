import os,sys,glob,time,collections,signal
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import random as random
import dimarray as da
import subprocess as sub
import scipy.stats as stats

sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
import __settings
model_dict=__settings.model_dict

try:
	model=sys.argv[1]
	print model
except:
	model='CAM4-2degree'

in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

try:
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
	working_path='data/'+model+'/'


if run_list==[]:
	run_list=['ens0030']


for cortype in ['corEKE','corSPI']:
	run_list=sorted([path.split('/')[-1].split('_')[-2] for path in glob.glob(working_path+scenario+'/'+cortype+'*.nc')])

	summary=da.DimArray(axes=[run_list,range(4),[-1,1],data.lat,data.lon],dims=['run','season','state','lat','lon'])

	for run in run_list:
		summary[run]=da.read_nc(working_path+scenario+'/corEKE_'+'_'.join([model,scenario,run])+'.nc')

	ds=dda.Dataset({cortype:summary})
	ds.write('data/'+model+'/'+'_'.join([cortype,model,scenario])+'.nc')
