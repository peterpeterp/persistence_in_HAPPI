import os,sys,glob,time,collections,gc,itertools
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import dimarray as da
from scipy import stats

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter/')

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

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

big_dict={}
for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	infile = 'data/'+dataset+'/'+dataset+'_regional_distrs_srex.pkl'
	pkl_file=open(infile, 'rb')
	big_dict[dataset] = pickle.load(pkl_file);	pkl_file.close()

models = ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']
regions = big_dict[dataset].keys()
scenarios = ['All-Hist','Plus20-Future','Plus15-Future']
states = big_dict[dataset]['CEU']['All-Hist'].keys()
seasons = big_dict[dataset]['CEU']['All-Hist']['warm'].keys()


D_stat = da.DimArray(axes=[models,regions,states,scenarios,scenarios], dims=['model','region','state','scenario-1','scenraio-2'])
p_value = da.DimArray(axes=[models,regions,states,scenarios,scenarios], dims=['model','region','state','scenario-1','scenraio-2'])

D_stat.values = 0
p_value.values = 1

for model in periods.model:
	for region in periods.region:
		for state in periods.state:
			for scenario1,scenario2 in [('All-Hist','Plus20-Future'),('All-Hist','Plus15-Future'),('Plus20-Future','Plus15-Future')]:
				distr_1 = counter_to_list(big_dict[model][region][scenario1][state]['JJA']['counter'])[1]
				distr_2 = counter_to_list(big_dict[model][region][scenario2][state]['JJA']['counter'])[1]
				ks_test = stats.ks_2samp(distr_1,distr_2)
				D_stat[model,region,state,scenario1,scenario2] = ks_test[0]
				D_stat[model,region,state,scenario2,scenario1] = ks_test[0]
				p_value[model,region,state,scenario1,scenario2] = ks_test[1]
				p_value[model,region,state,scenario2,scenario1] = ks_test[1]
				print(model,region,state,scenario1,scenario2,ks_test[1])

				gc.collect()

da.Dataset({'p-value':p_value,'D-stat':D_stat}).write_nc('data/reg_KS-test.nc')











#
