import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import dimarray as da
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
sys.path.append('/Users/peterpfleiderer/Documents/Projects/Persistence/weather_persistence/')
import persistence_support as persistence_support; reload(persistence_support)
from persistence_support import *

model=sys.argv[1]
print model

try:
	region=sys.argv[2]
except: region=None

try:
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
	scenarios=['Plus20-Future','Plus15-Future','All-Hist']
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
	working_path='/Users/peterpfleiderer/Documents/Projects/Persistence/data/'+model+'/'
	scenarios=['All-Hist']

overwrite=True
os.system('mkdir '+working_path+'/regional')

pkl_file = open('data/SREX.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()



print srex.keys()

def create_regional_distr(region):
	out_file=working_path+'/regional/'+region+'_'+model+'_summer.nc'
	if overwrite and os.path.isfile(out_file): os.system('rm '+out_file)
	if os.path.isfile(out_file)==False:
		print region
		tmp={}
		for scenario in scenarios:
			print working_path+'/'+model+'_'+scenario+'_summerQ90.nc'
			data=da.read_nc(working_path+'/'+model+'_'+scenario+'_summerQ90.nc')

			tmp[scenario]={'x90_cum_temp':np.array([]),'x90_mean_temp':np.array([]),'x90_hottest_day_shift':np.array([]),'x90_hottest_day':np.array([]),'TXx_in_x90':np.array([])}
			polygon=Polygon(srex[region]['points'])
			for x in data.lon:
				if x>180:
					x__=x-360
				else:
					x__=x
				for y in data.lat:
					if polygon.contains(Point(x__,y)):
						for var in tmp[scenario].keys():
							tmp[scenario][var]=np.append(tmp[scenario][var],data[var][:,:,y,x].flatten())

		n_events=0
		for var in ['x90_hottest_day','x90_cum_temp','x90_mean_temp','x90_hottest_day_shift']:
			for scenario in scenarios:
				if len(tmp[scenario][var])>n_events:
					n_events=len(tmp[scenario][var])

		reg_dict={}
		for var in ['x90_hottest_day','x90_cum_temp','x90_mean_temp','x90_hottest_day_shift']:
			reg_dict[var]=da.DimArray(axes=[np.asarray(scenarios),np.array(range(n_events))],dims=['scenario','ID'])
			for scenario in scenarios:
				reg_dict[var][scenario,0:len(tmp[scenario][var])-1]=tmp[scenario][var]

		n_events=0
		for scenario in scenarios:
			if len(tmp[scenario]['TXx_in_x90'])>n_events:
				n_events=len(tmp[scenario]['TXx_in_x90'])

		reg_dict['TXx_in_x90']=da.DimArray(axes=[np.asarray(scenarios),np.array(range(n_events))],dims=['scenario','ID'])
		for scenario in scenarios:
			reg_dict['TXx_in_x90'][scenario,0:len(tmp[scenario]['TXx_in_x90'])-1]=tmp[scenario]['TXx_in_x90']

		ds=da.Dataset(reg_dict)
		ds.write_nc(working_path+'/regional/'+region+'_'+model+'_summer.nc', mode='w')


if region is None:
	for region in srex.keys():
		create_regional_distr(region)
else:
	create_regional_distr(region)
