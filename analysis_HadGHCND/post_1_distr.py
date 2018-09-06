import os,sys,glob,time,collections,gc,pickle
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HadGHCND_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

seasons={'MAM':{'months':[3,4,5],'index':0}, 'JJA':{'months':[6,7,8],'index':1}, 'SON':{'months':[9,10,11],'index':2}, 'DJF':{'months':[12,1,2],'index':3}}

file='data/HadGHCND_TMean_grided.1950-2014_period.nc'

nc_in=Dataset(file,'r')
lat=nc_in.variables['lat'][:]
lon=nc_in.variables['lon'][:]

distr_dict={}
for y in lat:
	for x in lon:
		distr_dict[str(y)+'_'+str(x)]={'MAM':collections.Counter(),'JJA':collections.Counter(),'SON':collections.Counter(),'DJF':collections.Counter()}



period_length=nc_in.variables['period_length'][:,:,:]
period_season=nc_in.variables['period_season'][:,:,:]

for iy in range(len(lat)):
	sys.stdout.write('.')	;	sys.stdout.flush()
	for ix in range(len(lon)):
		for season in seasons.keys():
			in_season=np.where(period_season[:,iy,ix]==seasons[season]['index'])[0]
			distr_dict[str(lat[iy])+'_'+str(lon[ix])][season]+=collections.Counter(period_length[:,iy,ix][in_season])


distr_dict['lon']=lon
distr_dict['lat']=lat

output = open('data/'+'HadGHCND'+'_counter.pkl', 'wb')
pickle.dump(distr_dict, output)
output.close()



# pkl_file = open('Nat-Hist_summary.pkl', 'rb')
# out_dict = pickle.load(pkl_file)	;	pkl_file.close()  



















