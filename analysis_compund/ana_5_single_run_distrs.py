import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import dimarray as da

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
sys.path.append('/Users/peterpfleiderer/Projects/Persistence/weather_persistence/')
import persistence_support as persistence_support; reload(persistence_support)
from persistence_support import *

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
	model='CAM4-2degree'
	scenario='All-Hist'
	working_path='data/'+model+'/'
except:
	os.chdir('/global/homes/p/pepflei/')
	model=sys.argv[1]
	scenario=sys.argv[2]
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'

sys.path.append('persistence_in_models/')
import __settings
model_dict=__settings.model_dict
grid=model_dict[model]['grid']

print model,scenario

masks=da.read_nc('masks/srex_mask_'+grid+'.nc')


for style,style_orig in zip(['tas','cpd','pr'],['tas','compound','pr']):
	run_list=[]
	for file in sorted(glob.glob(working_path+'/'+scenario+'/'+style_orig+'_*_period.nc')):
		run_list.append(file.split('_')[-2])

	distrs = da.DimArray(axes=[['ENA','CAS','NAS','CAM','CNA','NEU','WAS','TIB','CGI','MED','WNA','ALA','CEU','EAS','NHml'],[1,3],[-1,1],run_list,range(1,36)],\
						 dims=['region','season','state','run','length'])

	for file in sorted(glob.glob(working_path+'/'+scenario+'/'+style_orig+'_*_period.nc')):
		run = file.split('_')[-2]

		print(file)
		nc=da.read_nc(file)

		for name in ['ENA','CAS','NAS','CAM','CNA','NEU','WAS','TIB','CGI','MED','WNA','ALA','CEU','EAS']:
			in_region = np.where(masks[name]>0)

			for sea in [1,3]:
				for st in [-1,1]:
					counter = collections.Counter()
					for y,x in zip(in_region[0],in_region[1]):
						season = nc['period_season'].ix[:,y,x].values
						state = nc['period_state'].ix[:,y,x].values
						per = nc['period_length'].ix[:,y,x].values
						in_seas_state=np.where((season==sea) & (state==st))[0]
						counter+=collections.Counter(per[in_seas_state])

					for len,count in counter.items():
						if len*st<=35:
							distrs[name,sea,st,run,len*st] = np.array([ float(count) / float(np.sum(counter.values()))])

		lats = nc.lat[(nc.lat>=35) & (nc.lat<=60)]
		for sea in [1,3]:
			for st in [-1,1]:
				counter = collections.Counter()
				for y in nc.lat[(nc.lat>=35) & (nc.lat<=60)]:
					for x in nc.lon:
						season = nc['period_season'][:,y,x].values
						state = nc['period_state'][:,y,x].values
						per = nc['period_length'][:,y,x].values
						in_seas_state=np.where((season==sea) & (state==st))[0]
						counter+=collections.Counter(per[in_seas_state])

				for len,count in counter.items():
					if len*st<=35:
						distrs['NHml',sea,st,run,len*st] = np.array([ float(count) / float(np.sum(counter.values()))])


		gc.collect()

	da.Dataset({'distrs':distrs}).write_nc('data/'+model+'/'+style+'_'+model+'_'+scenario+'_distrs.nc')