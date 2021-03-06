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

for cortype in ['corEKE','corSPI']:
	run_list=sorted([path.split('/')[-1].split('_')[-1].split('.')[0] for path in glob.glob(working_path+'All-Hist'+'/'+cortype+'*.nc')])
	example_data=da.read_nc(working_path+'All-Hist'+'/'+cortype+'_'+'_'.join([model,'All-Hist',run_list[0]])+'.nc')
	all_runs={'corrcoef':da.DimArray(axes=[run_list,['All-Hist','Plus20-Future'],range(4),[-1,1],example_data.lat,example_data.lon],dims=['run','scenario','season','state','lat','lon']),
			'p_value':da.DimArray(axes=[run_list,['All-Hist','Plus20-Future'],range(4),[-1,1],example_data.lat,example_data.lon],dims=['run','scenario','season','state','lat','lon'])}
	for scenario in ['All-Hist','Plus20-Future']:
		for run in run_list:
			if os.path.isfile(working_path+scenario+'/'+cortype+'_'+'_'.join([model,scenario,run])+'.nc'):
				tmp=da.read_nc(working_path+scenario+'/'+cortype+'_'+'_'.join([model,scenario,run])+'.nc')
				all_runs['corrcoef'][run,scenario]=tmp['corrcoef']
				all_runs['p_value'][run,scenario]=tmp['p_value']

	ds=da.Dataset({cortype:all_runs})
	ds.write('data/'+model+'/'+'_'.join([cortype,model])+'_all_runs.nc')

	summary=da.DimArray(axes=[['All-Hist','Plus20-Future'],range(4),[-1,1],['corrcoef_mn','corrcoef_std','p_value_mn','p_value_std'],example_data.lat,example_data.lon],dims=['scenario','season','state','statistic','lat','lon'])
	summary[:,:,:,'corrcoef_mn',:,:]=all_runs['corrcoef'].mean(axis=0)
	summary[:,:,:,'corrcoef_std',:,:]=all_runs['corrcoef'].std(axis=0)
	summary[:,:,:,'p_value_mn',:,:]=all_runs['p_value'].mean(axis=0)
	summary[:,:,:,'p_value_std',:,:]=all_runs['p_value'].std(axis=0)

	ds=da.Dataset({cortype:summary})
	ds.write('data/'+model+'/'+'_'.join([cortype,model])+'_summary.nc')
