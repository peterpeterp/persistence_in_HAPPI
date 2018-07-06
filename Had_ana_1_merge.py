import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle

model='HadGHCND'
print(model)

overwrite=True

os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence')

seasons={'MAM':{'months':[3,4,5],'index':0}, 'JJA':{'months':[6,7,8],'index':1}, 'SON':{'months':[9,10,11],'index':2}, 'DJF':{'months':[12,1,2],'index':3}}


all_files=glob.glob('data/HadGHCND/All-Hist/*period*')

print(all_files)

nc_in=Dataset(all_files[0],'r')
lat=nc_in.variables['lat'][:]
lon=nc_in.variables['lon'][:]
nc_in.close()

for scenario,years in zip(['1954-1974','1990-2010','All-Hist'],[[1954,1974],[1990,2010],[1950,2014]]):
	distr_dict={}
	for y in lat:
		for x in lon:
			distr_dict[str(y)+'_'+str(x)]={'MAM':collections.Counter(),'JJA':collections.Counter(),'SON':collections.Counter(),'DJF':collections.Counter()}

	for file in all_files:
		start_time=time.time()
		print(file)
		nc_in=Dataset(file,'r')
		period_length=nc_in.variables['period_length'][:,:,:]
		period_season=nc_in.variables['period_season'][:,:,:]
		period_midpoint=nc_in.variables['period_midpoints'][:,:,:]

		for iy in range(len(lat)):
			sys.stdout.write('.')	;	sys.stdout.flush()
			for ix in range(len(lon)):
				for season in seasons.keys():
					in_period=np.where((period_midpoint[:,iy,ix]>=years[0]) & (period_midpoint[:,iy,ix]<=years[1]))[0]
					in_season=np.where(period_season[in_period,iy,ix]==seasons[season]['index'])[0]
					distr_dict[str(lat[iy])+'_'+str(lon[ix])][season]+=collections.Counter(period_length[:,iy,ix][in_season])


		print(time.time()-start_time)

	distr_dict['lon']=lon
	distr_dict['lat']=lat

	output = open('data/'+model+'/'+model+'_'+scenario+'_counter.pkl', 'wb')
	pickle.dump(distr_dict, output)
	output.close()
