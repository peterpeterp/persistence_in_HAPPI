import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import cPickle as pickle

import init_dirs as init


model=sys.argv[1]
print model
working_path='/global/cscratch1/sd/pepflei/'+model+'/regional/'

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

summary=da.DimArray(axes=[['Plus20-Future','Plus15-Future','All-Hist'],list(srex.keys()),['90X_cum_heat','90X_hot_shift','90X_hot_temp','90X_mean_temp','frac_pos_shift','frac_neg_shift'],['mean','qu_0','qu_66l','qu_25','qu_50','qu_75','qu_66h','qu_100']],dims=['scenario','region','variable','stat'])
for region in summary.region:
    dat=da.read_nc(working_path+region+'_'+model+'_summer.nc')
    for var in ['90X_mean_temp','90X_cum_heat','90X_hot_shift','90X_hot_temp']:
        for scenario in summary.scenario:
            values=dat[var][scenario,:].values
            values=values[np.isfinite(values)]
            summary[scenario,region,var,'mean']=np.nanmean(values,axis=1)
            for qu,qu_name in zip([0,1/6.*100,25,50,75,5/6.*100,100],['mean','qu_0','qu_66l','qu_25','qu_50','qu_75','qu_66h','qu_100']):
                summary[scenario,region,var,qu_name]=np.nanpercentile(values,qu,axis=1)

    for scenario in summary.scenario:
        summary[scenario,region,'frac_pos_shift','mean']=len(np.where(dat['90X_hot_shift'][scenario,:]>0)[0])/float(dat['90X_hot_shift'].shape[1])
        summary[scenario,region,'frac_neg_shift','mean']=len(np.where(dat['90X_hot_shift'][scenario,:]<0)[0])/float(dat['90X_hot_shift'].shape[1])

ds=da.Dataset({'summerStats':summary})
ds.write_nc('data/'+model+'_SummarySummer.nc', mode='w')
