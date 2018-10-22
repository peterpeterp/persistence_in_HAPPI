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
scenarios = ['All-Hist','Plus20-Future']
styleStates = ['tas_warm','pr_dry','cpd_dry-warm']

out_file={
	'model' : da.DimArray(models,axes=[models],dims=['model']),
	'scenario' : da.DimArray(scenarios,axes=[scenarios],dims=['scenario']),
}

masks = da.read_nc('masks/srex_mask_'+model_dict['MIROC5']['grid']+'.nc')
regions = masks.keys()+['NHml']
out_file['EKE'] = da.DimArray(axes=[models,scenarios,regions],dims=['model','scenario','region'])

for model in models:
	print('**************'+model+'**************')
	masks_in = da.read_nc('masks/srex_mask_'+model_dict[model]['grid']+'.nc')
	masks = {}
	for name,mask in masks_in.items():
		mask[mask!=0] = 1
		mask[mask==0] = np.nan
		masks[name] = mask.copy()
		masks[name].lat = np.round(masks[name].lat,03)
		masks[name].lon = np.round(masks[name].lon,03)

	for scenario in scenarios:
		EKE = da.read_nc('data/EKE/*'+scenario+'*'+model+'*_monClim.nc')['EKE'].squeeze()

		for region in masks.keys():
			out_file['EKE'][model,scenario,region] = np.nanmean(np.nanmean(EKE.values[6:9,:,:],axis=0) * masks[region].values)
			print(region, np.nanmean(np.nanmean(EKE.values[6:9,:,:]) * masks[region].values))
		out_file['EKE'][model,scenario,'NHml'] = np.nanmean(EKE[:,35:60,:].values[5:8,:,:])

out_file = da.Dataset(out_file)
out_file.write_nc('data/EKE_summerMean_srex.nc','w')
