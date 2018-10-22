import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import dimarray as da

try:
	os.chdir('/global/homes/p/pepflei/')
except:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')

sys.path.append('weather_persistence/')
import persistence_support as persistence_support; reload(persistence_support)
from persistence_support import *

sys.path.append('persistence_in_models/')
import __settings
model_dict=__settings.model_dict

models = ['CAM4-2degree','MIROC5','NorESM1','ECHAM6-3-LR']
scenarios = ['All-Hist','Plus20-Future','Plus15-Future']

out_file={
	'length' : da.DimArray(['7','14','21','28'],axes=[['7','14','21','28']],dims=['length']),
	'model' : da.DimArray(models,axes=[models],dims=['model']),
	'scenario' : da.DimArray(scenarios,axes=[scenarios],dims=['scenario']),
}

masks = da.read_nc('masks/srex_mask_'+model_dict['MIROC5']['grid']+'.nc')
regions = masks.keys()+['NHml']
for var in ['hottest_day','hottest_day_shift','mean_temp']:
	out_file[var] = da.DimArray(axes=[models,scenarios,regions,['7','14','21','28']],dims=['model','scenario','region','length'])

out_file['seasMean'] = da.DimArray(axes=[models,scenarios,regions],dims=['model','scenario','region'])

for model in models:
	masks = da.read_nc('masks/srex_mask_'+model_dict[model]['grid']+'.nc')
	for scenario in scenarios:
		summerStat = da.read_nc('data/'+model+'/summer/tas_'+model+'_'+scenario+'_summerStat.nc')
		seasMean = da.read_nc('data/'+model+'/summer/tas_'+model+'_'+scenario+'_seasMean.nc')['tas'].squeeze().ix[2]

		for var in ['hottest_day','hottest_day_shift','mean_temp']:
			for region in masks.keys():
				out_file[var][model,scenario,region,:].values = np.nanmean(summerStat[var] * masks[region], axis=(1,2))
			out_file[var][model,scenario,'NHml',:].values = np.nanmean(summerStat[var][:,35:60,:], axis=(1,2))


		for region in masks.keys():
			out_file['seasMean'][model,scenario,region] = np.nanmean(seasMean * masks[region])
		out_file['seasMean'][model,scenario,'NHml'] = np.nanmean(seasMean[35:60,:])

out_file = da.Dataset(out_file)
out_file.write_nc('data/tas_summerStat_srex.nc','w')
