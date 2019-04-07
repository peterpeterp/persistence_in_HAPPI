import os,sys,glob,time,collections,signal,gc
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import subprocess as sub

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

def counter_to_list(counter):
	tmp=[]
	lengths=counter.keys()
	if 0 in lengths:
		lengths.remove(0)
	if len(lengths)>2:
		for key in lengths:
			for i in range(counter[key]):
				tmp.append(key)
		tmp=np.array(tmp)
		return -tmp[tmp<0],tmp[tmp>0]
	else:
		return [],[]

def quantile_from_cdf(x,qu):
	counts, bin_edges = np.histogram(x, bins=range(0,max(x)+1), normed=True)
	cdf = np.cumsum(counts)

	quantiles=[]
	for q in qu:
		if q>=1:q/=100.
		x1=np.where(cdf<q)[0][-1]
		quantiles.append(x1+(q-cdf[x1])/(cdf[x1+1]-cdf[x1]))

	return quantiles

summary = da.read_nc('data/cor_reg_summary.nc')['summary_cor']
artificial = da.DimArray(axes = [['Plus20-Artificial-v1'],['CAM4-2degree','MIROC5','ECHAM6-3-LR','NorESM1'], ['dry','5mm'], summary.region, summary.season, ['mean','qu_1','qu_5','qu_10','qu_25','qu_50','qu_75','qu_90','qu_95','qu_99']], dims = ['scenario','model','state','region','season','statistic'])

for model in artificial.model:
	for scenario in artificial.scenario:
		for state in artificial.state:
			for region in artificial.region:
				for season in artificial.season:
					neg,pos=counter_to_list(tmp[region][scenario][state][season]['counter'])
					artificial[scenario,model,state,region,season,'mean'] = np.nanmean(pos)
					artificial[scenario,model,state,region,season][['qu_1','qu_5','qu_10','qu_25','qu_50','qu_75','qu_90','qu_95','qu_99']] = quantile_from_cdf(pos,[1.,5.,10.,25.,50.,75.,90.,95.,99.])

da.Dataset({'artificial_summary':artificial}).write_nc('data/artificial/reg_summary_mean_qu_artificial.nc')

#
#
# summary = da.read_nc('data/cor_reg_summary.nc')['summary_cor']
# artificial = da.DimArray(axes = [['Plus20-Artificial-v1'],['CAM4-2degree','MIROC5','ECHAM6-3-LR','NorESM1'], ['dry','5mm'], summary.region, summary.season, ['mean','qu_1','qu_5','qu_10','qu_25','qu_50','qu_75','qu_90','qu_95','qu_99']], dims = ['scenario','model','state','region','season','statistic'])
#
# for scenario in artificial.scenario:
# 	for model in artificial.model:
# 		tmp = pickle.load(open('data/artificial/'+model+'_regional_distrs_srex_artificial.pkl', 'rb'))
#
# 		for state in artificial.state:
# 			for region in artificial.region:
# 				for season in artificial.season:
# 					neg,pos=counter_to_list(tmp[region][scenario][state][season]['counter'])
# 					artificial[scenario,model,state,region,season,'mean'] = np.nanmean(pos)
# 					artificial[scenario,model,state,region,season][['qu_1','qu_5','qu_10','qu_25','qu_50','qu_75','qu_90','qu_95','qu_99']] = quantile_from_cdf(pos,[1.,5.,10.,25.,50.,75.,90.,95.,99.])
#
# da.Dataset({'artificial_summary':artificial}).write_nc('data/artificial/reg_summary_mean_qu_artificial.nc')
#
#
#



#
