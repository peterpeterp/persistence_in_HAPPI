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

for model in ['CAM4-2degree','MIROC5','NorESM1','ECHAM6-3-LR']:
	masks = da.read_nc('masks/srex_mask_'+model_dict[model]['grid']+'.nc')
	for scenario in ['Plus20-Future','Plus15-Future','All-Hist']:
		summerStat = da.read_nc('data/'+model+'/tas_'+model+'_'+scenario+'_summerStat.nc')
		seasMean = da.read_nc('data/'+model+'/tas_'+model+'_'+scenario+'_seasMean.nc')

		out_file={
			'length' : da.DimArray(['7','14','21','28'],axes=[['7','14','21','28']],dims=['length']),
		}

		for var in ['hottest_day','hottest_day_shift','mean_temp']:
			out_file[var] = da.DimArray(axes=[masks.keys(),['7','14','21','28']],dims=['region','length'])
			for region in masks.keys():
				out_file[var][region,:] = np.nanmean(summerStat[var] * masks[region], axis=(1,2))
			np.nanmean(summerStat[var][:,35:60,:], axis=(1,2))

			out_file[var] = da.DimArray(axes=[masks.keys(),['7','14','21','28']],dims=['region','length'])
			for region in masks.keys():
				out_file[var][region,:] = np.nanmean(summerStat[var] * masks[region], axis=(1,2))
			np.nanmean(summerStat[var][:,35:60,:], axis=(1,2))

		out_file = da.Dataset(out_file)
		out_file.write_nc('data/'+model+'/tas_'+model+'_'+scenario+'_summerStat_srex.nc','w')
