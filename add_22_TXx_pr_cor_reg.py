import os,sys,glob,time,collections
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import random as random
import dimarray as da
import subprocess

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
	sys.path.append('/Users/peterpfleiderer/Documents/Projects/Persistence/persistence_in_models/')
except:
	os.chdir('/global/homes/p/pepflei/')
	sys.path.append('/global/homes/p/pepflei/persistence_in_models/')


import __settings
model_dict=__settings.model_dict



mask=da.read_nc('masks/srex_mask_64x128.nc')
regions=[reg for reg in mask.keys() if '*' not in reg]
out=da.DimArray(dims=['model','scenario','season','region','stat'],axes=[model_dict.keys(),['Plus20-Future','Plus15-Future','All-Hist'],['JJA','DJF'],regions,['mean','0','0.05','1/6','0.5','5/6.','0.95','1']])

for model in out.model:
	working_path='/global/cscratch1/sd/pepflei/TXx_pr_cor/'+model+'/'
	grid=model_dict[model]['grid']

	masks=da.read_nc('../masks/srex_mask_'+model+'.nc')

	for scenario,selyears in out.scenario:
		for seas in out.season:
			cor=da.read_nc(working_path+'corTXxPr_'+model+'_'+scenario+'_'+seas+'.nc')
			for reg in out.region:
				mask=masks['CEU']
				mask[mask>0]=1
				mask[mask==0]=np.nan
				values=cor.copy()*mask
				out[model,scenario,seas,reg,'mean']=np.nanmean(values)
				out[model,scenario,seas,reg,['0','0.05','1/6','0.5','5/6.','0.95','1']]=np.nanpercentile(values,[0,5,1/6.*100,50,5/6.*100,95,100])
