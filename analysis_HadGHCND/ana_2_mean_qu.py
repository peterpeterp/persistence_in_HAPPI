import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import dimarray as da

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HadGHCND_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')


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


scenarios=['All-Hist']
seasons=['MAM','JJA','SON','DJF','year']
states=['cold','warm']
types=['mean','qu_1','qu_5','qu_10','qu_25','qu_50','qu_75','qu_90','qu_95','qu_99']

pkl_file = open('data/HadGHCND_counter.pkl', 'rb')
hadghcnd = pickle.load(pkl_file)	;	pkl_file.close()  

lat=hadghcnd['lat']
lon=hadghcnd['lon']

SummaryMeanQu=da.DimArray(axes=[np.asarray(scenarios),np.asarray(seasons),np.asarray(states),np.asarray(types),lat,lon],dims=['scenario','season','state','type','lat','lon'])


for iy in range(len(lat)):
	for ix in range(len(lon)):
		grid_cell=hadghcnd[str(lat[iy])+'_'+str(lon[ix])]
		grid_cell['year']=grid_cell['MAM']+grid_cell['JJA']+grid_cell['SON']+grid_cell['DJF']

for season in seasons:
	print season
	for iy in range(len(lat)):
		print iy
		for ix in range(len(lon)):
			counter=hadghcnd[str(lat[iy])+'_'+str(lon[ix])][season]
			if len(counter)>5:
				cold,warm=counter_to_list(counter)
				for state_name,distr in zip(['cold','warm'],[cold,warm]):
					SummaryMeanQu['All-Hist'][season][state_name]['mean'][lat[iy]][lon[ix]]=np.mean(distr)
					SummaryMeanQu['All-Hist'][season][state_name].ix[1:10,iy,ix]=np.percentile(distr,[1.,5.,10.,25.,50.,75.,90.,95.,99.])

ds=da.Dataset({'SummaryMeanQu':SummaryMeanQu})
ds.write_nc('data/HadGHCND_SummaryMeanQu.nc', mode='w')











