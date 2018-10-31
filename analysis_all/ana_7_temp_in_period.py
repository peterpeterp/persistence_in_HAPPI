import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle

model=sys.argv[1]
print model

overwrite=True

working_path='/global/cscratch1/sd/pepflei/'+model+'/'

seasons={'MAM':{'months':[3,4,5],'index':0}, 'JJA':{'months':[6,7,8],'index':1}, 'SON':{'months':[9,10,11],'index':2}, 'DJF':{'months':[12,1,2],'index':3}}

for scenario in ['Plus20-Future','All-Hist']:
	all_files=glob.glob(working_path+scenario+'/'+style+'*period.nc')

	print all_files
	for filename in all_files:
		start_time=time.time()
		print file
		nc_period=da.read_nc(filename)
		per_len = nc_period['period_length']
		per_mid = nc_period['period_midpoints']
		per_seas = nc_period['period_season']

		print time.time()-start_time

	distr_dict['lon']=lon
	distr_dict['lat']=lat

	output = open('../data/'+model+'/'+style+'_'+model+'_'+scenario+'_counter.pkl', 'wb')
	pickle.dump(distr_dict, output)
	output.close()
