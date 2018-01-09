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

pkl_file = open('data/SREX.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

summary=da.DimArray(axes=[['Plus20-Future','Plus15-Future','All-Hist'],list(srex.keys()),['x90_hottest_day','x90_cum_temp','x90_mean_temp','x90_hottest_day_shift','frac_pos_shift','frac_neg_shift','frac_TXx_in_X90'],['mean','qu_0','qu_66l','qu_25','qu_50','qu_75','qu_66h','qu_100']],dims=['scenario','region','variable','stat'])
for region in summary.region:
    dat=da.read_nc(working_path+region+'_'+model+'_summer.nc')
    for var in ['x90_hottest_day','x90_cum_temp','x90_mean_temp','x90_hottest_day_shift']:
        summary[:,region,var,'mean']=np.nanmean(dat[var],axis=1)
        for qu,qu_name in zip([0,1/6.*100,25,50,75,5/6.*100,100],['qu_0','qu_66l','qu_25','qu_50','qu_75','qu_66h','qu_100']):
            summary[:,region,var,qu_name]=np.nanpercentile(dat[var],qu,axis=1)

    print region
    for scenario in summary.scenario:
        print scenario
        tmp=dat['x90_hottest_day_shift'][scenario,:].values
        tmp=tmp[np.isfinite(tmp)]
        summary[scenario,region,'frac_pos_shift','mean']=len(np.where(tmp>0)[0])/float(len(tmp))
        summary[scenario,region,'frac_neg_shift','mean']=len(np.where(tmp<0)[0])/float(len(tmp))
        print len(tmp),len(np.where(tmp>0)[0]),len(np.where(tmp<0)[0])

    for scenario in summary.scenario:
        print scenario
        tmp=dat['TXx_in_x90'][scenario,:].values
        tmp=tmp[np.isfinite(tmp)]
        summary[scenario,region,'frac_TXx_in_X90','mean']=len(np.where(tmp==1)[0])/float(tmp.shape[0])
        print len(np.where(tmp==1)[0]),len(np.where(tmp==0)[0]),float(tmp.shape[0]),len(np.where(tmp)[0])/float(tmp.shape[0])

ds=da.Dataset({'summerStats':summary})
ds.write_nc('data/'+model+'/'+model+'_SummarySummer.nc', mode='w')
