import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import dimarray as da

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')


def counter_to_count(counter):
	tmp=0
	lengths=counter.keys()
	if 0 in lengths:
		lengths.remove(0)
	if len(lengths)>2:
		for key in lengths:
			for i in range(counter[key]):
				tmp+=key
		tmp=np.array(tmp)
		return tmp
	else:
		return 0


model=sys.argv[1]
print model

scenarios=['All-Hist','Plus15-Future','Plus20-Future']
seasons=['MAM','JJA','SON','DJF','year']

state_dict = {
	'warm':'tas',
	'dry':'pr',
	'5mm':'pr',
	'10mm':'pr',
	'dry-warm':'cpd',
	}

for state,style in state_dict.items():

	big_dict={}
	for scenario in scenarios:
		pkl_file = open('data/'+model+'/'+style+'_'+model+'_'+scenario+'_'+state+'_counter.pkl', 'rb')
		big_dict[scenario] = pickle.load(pkl_file)	;	pkl_file.close()

	lat=big_dict[scenario]['lat']
	lon=big_dict[scenario]['lon']

	if 'SummaryMeanQu' not in globals():
		SummaryMeanQu=da.DimArray(axes=[np.asarray(scenarios),np.asarray(seasons),np.asarray(state_dict.keys()),lat,lon], dims=['scenario','season','state','lat','lon'])

	for scenario in scenarios:
		distr_dict = big_dict[scenario]

		for iy in range(len(lat)):
			for ix in range(len(lon)):
				grid_cell=distr_dict[str(lat[iy])+'_'+str(lon[ix])]
				grid_cell['year']=grid_cell['MAM']+grid_cell['JJA']+grid_cell['SON']+grid_cell['DJF']

		for season in seasons:
			print season
			for iy in range(len(lat)):
				sys.stdout.write('.')	;	sys.stdout.flush()
				for ix in range(len(lon)):
					counter=distr_dict[str(lat[iy])+'_'+str(lon[ix])][season]
					if len(counter)>3:
						SummaryMeanQu[scenario,season,state,lat[iy],lon[ix]]=counter_to_count(counter)

ds=da.Dataset({'SummaryMeanQu':SummaryMeanQu})
ds.write_nc('data/'+model+'/'+model+'_StateCount.nc', mode='w')
