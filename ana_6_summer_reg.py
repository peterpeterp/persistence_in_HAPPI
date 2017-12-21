import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import dimarray as da
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
sys.path.append('/Users/peterpfleiderer/Documents/Projects/weather_persistence/')
import persistence_support as persistence_support; reload(persistence_support)
from persistence_support import *

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

try:
	model=sys.argv[1]
	print model
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
except:
	model='ECHAM6-3-LR'
	working_path='data/tests/'

overwrite=False
os.system('mkdir '+working_path+'/regional')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

scenarios=['Plus20-Future','Plus15-Future','All-Hist']

for region in srex.keys():
	out_file=working_path+'/regional/'+region+'_'+model+'_summer.nc'
	if overwrite and os.path.isfile(out_file): os.system('rm '+out_file)
	if os.path.isfile(out_file)==False:
		print region
		tmp={}
		for scenario in scenarios:
			print working_path+'/'+model+'_'+scenario+'_summerQ90.nc'
			data=da.read_nc(working_path+'/'+model+'_'+scenario+'_summerQ90.nc')
			tmp[scenario]={'90X_cum_heat':np.array([]),'90X_hot_shift':np.array([]),'90X_hot_temp':np.array([]),'90X_mean_temp':np.array([])}
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
		for var in ['90X_cum_heat','90X_hot_shift','90X_hot_temp','90X_mean_temp']:
			for scenario in scenarios:
				if len(tmp[scenario][var])>n_events:
					n_events=len(tmp[scenario][var])

		reg_dict={}
		for var in ['90X_cum_heat','90X_hot_shift','90X_hot_temp','90X_mean_temp']:
			reg_dict[var]=da.DimArray(axes=[np.asarray(scenarios),np.array(range(n_events))],dims=['scenario','ID'])
			for scenario in scenarios:
				reg_dict[var][scenario,0:len(tmp[scenario][var])-1]=tmp[scenario][var]

		ds=da.Dataset(reg_dict)
		ds.write_nc(working_path+'/regional/'+region+'_'+model+'_summer.nc', mode='w')
