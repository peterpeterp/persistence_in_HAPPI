import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import dimarray as da

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

model='EOBS'

overwrite=True

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

working_path='data/EOBS/'

scenarios=['All-Hist']
seasons=['MAM','JJA','SON','DJF','year']

types=['mean','qu_1','qu_5','qu_10','qu_25','qu_50','qu_75','qu_90','qu_95','qu_99','npqu_1','npqu_5','npqu_10','npqu_25','npqu_50','npqu_75','npqu_90','npqu_95','npqu_99']

for style,states in zip(['tas','cpd','pr'],[['cold','warm'],['wet-cold','dry-warm'],['dry','wet']]):
	big_dict={}
	for scenario in ['All-Hist']:
		pkl_file = open('data/'+model+'/'+style+'_'+model+'_'+scenario+'_counter.pkl', 'rb')
		big_dict[scenario] = pickle.load(pkl_file)	;	pkl_file.close()

	lat=np.ma.getdata(big_dict[scenario]['lat'])
	lon=np.ma.getdata(big_dict[scenario]['lon'])

	SummaryMeanQu=da.DimArray(axes=[np.asarray(scenarios),np.asarray(seasons),np.asarray(states),np.asarray(types),lat,lon],dims=['scenario','season','state','type','lat','lon'])

	for scenario in ['All-Hist']:
		distr_dict = big_dict[scenario]

		for iy in range(len(lat)):
			for ix in range(len(lon)):
				grid_cell=distr_dict[str(lat[iy])+'_'+str(lon[ix])]
				grid_cell['year']=grid_cell['MAM']+grid_cell['JJA']+grid_cell['SON']+grid_cell['DJF']

		for season in seasons:
			print '\n'+season
			for iy in range(len(lat)):
				sys.stdout.write('.')	;	sys.stdout.flush()
				for ix in range(len(lon)):
					counter=distr_dict[str(lat[iy])+'_'+str(lon[ix])][season]
					if len(counter)>10:
						neg,pos=counter_to_list(counter)
						if len(dry)>10 and len(wet)>10:
							for state_name,distr in zip(states,[neg,pos]):
								SummaryMeanQu[scenario,season,state_name,'mean',lat[iy],lon[ix]]=np.mean(distr)
								#SummaryMeanQu[scenario][season][state_name].ix[1:10,iy,ix]=np.percentile(distr,[1.,5.,10.,25.,50.,75.,90.,95.,99.])
								try:
									SummaryMeanQu[scenario,season,state_name,['qu_1','qu_5','qu_10','qu_25','qu_50','qu_75','qu_90','qu_95','qu_99'],lat[iy],lon[ix]]=quantile_from_cdf(distr,[1.,5.,10.,25.,50.,75.,90.,95.,99.])
								except:
									pass
								SummaryMeanQu[scenario,season,state_name,['npqu_1','npqu_5','npqu_10','npqu_25','npqu_50','npqu_75','npqu_90','npqu_95','npqu_99'],lat[iy],lon[ix]]=np.nanpercentile(distr,[1.,5.,10.,25.,50.,75.,90.,95.,99.])

	ds=da.Dataset({'SummaryMeanQu':SummaryMeanQu})
	ds.write_nc('data/'+model+'/'+style+'_'+model+'_SummaryMeanQu.nc', mode='w')
