import os,sys,glob,time,collections,signal,gc
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import subprocess as sub

os.chdir('/Users/peterpfleiderer/Projects/Persistence/')

sys.path.append('persistence_in_models/')
from __settings import *


models=['ECHAM6-3-LR','MIROC5','NorESM1','CAM4-2degree']
scenarios=['All-Hist','Plus20-Future','Plus15-Future']
states=['warm','dry','dry-warm','5mm']
seasons=['JJA']
regions=['ENA','CAS','NAS','CNA','NEU','WAS','TIB','CGI','MED','WNA','ALA','CEU','EAS','mid-lat']


out = da.DimArray(axes=[models,seasons,states,regions,scenarios], dims=['model','season','state','region','scenario'])

for model in models:
	counts = da.read_nc('data/'+model+'/state_stats/'+model+'_stateCount_regridReady.nc')
	masks = da.read_nc('masks/srex_mask_'+model_dict[model]['grid']+'.nc')
	land_mask = da.read_nc('masks/landmask_'+model_dict[model]['grid']+'.nc')['landmask']

	for reg_name in regions:
		if reg_name != 'mid-lat':
			mask = masks[reg_name]
			mask[mask>0] = 1
			mask = np.array(mask * land_mask,np.bool)

		else:
			mask = np.zeros([len(counts.lat),len(counts.lon)])
			ml = np.where((counts.lat>=35) & (counts.lat<=60))[0]
			mask[ml,:] = 1
			mask = np.array(mask * land_mask,np.bool)

		for scenario in scenarios:
			for state in states:
				for season in seasons:
					tmp = counts['*'.join([scenario,season,state])]
					out[model,season,state,reg_name,scenario] = np.nanmean(tmp.ix[np.where(mask)[0],np.where(mask)[1]])


da.Dataset({'state_count':out}).write_nc('data/state_count_srex.nc')
