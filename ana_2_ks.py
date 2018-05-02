import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import dimarray as da
from scipy import stats


try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/')
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

model=sys.argv[1]
print model

scenarios=['Plus20-Future','Plus15-Future','All-Hist']
seasons=['MAM','JJA','SON','DJF','year']
states=['cold','warm']
types=['KS_vs_Plus20-Future','KS_vs_Plus15-Future','KS_vs_All-Hist']

big_dict={}
for scenario in ['All-Hist','Plus15-Future','Plus20-Future']:
	pkl_file = open('data/'+model+'/'+model+'_'+scenario+'_counter.pkl', 'rb')
	big_dict[scenario] = pickle.load(pkl_file)	;	pkl_file.close()

lat=big_dict[scenario]['lat']
lon=big_dict[scenario]['lon']

SummaryKS=da.DimArray(axes=[np.asarray(scenarios),np.asarray(seasons),np.asarray(states+'stateInd'),np.asarray(types),lat,lon],dims=['scenario','season','state','type','lat','lon'])

for scenario in scenarios:
	distr_dict = big_dict[scenario]

	for iy in range(len(lat)):
		for ix in range(len(lon)):
			grid_cell=distr_dict[str(lat[iy])+'_'+str(lon[ix])]
			grid_cell['year']=grid_cell['MAM']+grid_cell['JJA']+grid_cell['SON']+grid_cell['DJF']

for scenario_combi in [['Plus20-Future','All-Hist'],['Plus15-Future','All-Hist'],['Plus20-Future','Plus15-Future']]:
	scenario_1=scenario_combi[0]
	scenario_2=scenario_combi[1]

	for season in seasons:
		print season
		for iy in range(len(lat)):
			print iy
			for ix in range(len(lon)):
				counter_1=big_dict[scenario_1][str(lat[iy])+'_'+str(lon[ix])][season]
				counter_2=big_dict[scenario_2][str(lat[iy])+'_'+str(lon[ix])][season]
				if len(counter_1)>5 and len(counter_2)>5:
					cold_1,warm_1=counter_to_list(counter_1)
					cold_2,warm_2=counter_to_list(counter_2)

					ks_cold=stats.ks_2samp(cold_1, cold_2)[1]
					ks_warm=stats.ks_2samp(warm_1, warm_2)[1]

					stateInd_1=np.append(cold_1,warm_1)
					stateInd_2=np.append(cold_2,warm_2)
					ks_stateInd=stats.ks_2samp(stateInd_1, stateInd_2)[1]

					for scenario_store in scenario_combi:
						for scenario_compare_to in scenario_combi:
							if scenario_store!=scenario_compare_to:
								SummaryKS[scenario_store][season]['cold']['KS_vs_'+scenario_compare_to][lat[iy]][lon[ix]]=ks_cold
								SummaryKS[scenario_store][season]['warm']['KS_vs_'+scenario_compare_to][lat[iy]][lon[ix]]=ks_warm
								SummaryKS[scenario_store][season]['stateInd']['KS_vs_'+scenario_compare_to][lat[iy]][lon[ix]]=ks_stateInd

ds=da.Dataset({'SummaryKS':SummaryKS})
ds.write_nc('data/'+model+'/'+model+'_SummaryKS.nc', mode='w')
