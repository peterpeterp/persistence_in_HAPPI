import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import cPickle as pickle

import init_dirs as init

try:
	model=sys.argv[1]
	print model
	working_path=init.model_dict[model]['path']+'regional/'
except:
	model='ECHAM6-3-LR'
	working_path='data/tests/'

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

summary=da.DimArray(axes=[np.asarray(['Plus20-Future','Plus15-Future','All-Hist']),np.array(srex.keys()),np.asarray(['mean_hot_shift','frac_pos_shift','mean_hot_temp','mean_cum_heat'])],dims=['scenario','region','stat'])
for region in summary.region:
    dat=da.read_nc(working_path+region+'_'+model+'_summer.nc')
    summary[:,region,'mean_hot_shift']=dat['90X_hot_shift'].mean(axis='ID', skipna=True)
    summary[:,region,'mean_hot_temp']=dat['90X_hot_temp'].mean(axis='ID', skipna=True)
    summary[:,region,'mean_cum_heat']=dat['90X_cum_heat'].mean(axis='ID', skipna=True)
    for scenario in summary.scenario:
        summary[scenario,region,'frac_pos_shift']=len(np.where(dat['90X_hot_shift'][scenario,:]>0)[0])/float(dat['90X_hot_shift'].shape[1])

ds=da.Dataset({'summerStats':summary})
ds.write_nc('data/'+model+'_SummarySummer.nc', mode='w')
