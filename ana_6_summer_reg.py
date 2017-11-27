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

model_dict={'MIROC5':{'grid':'128x256','path':'/global/cscratch1/sd/pepflei/MIROC/MIROC5/'},
			'NorESM1':{'grid':'192x288','path':'/global/cscratch1/sd/pepflei/NCC/NorESM1-HAPPI/'},
			'ECHAM6-3-LR':{'grid':'96x192','path':'/global/cscratch1/sd/pepflei/MPI-M/ECHAM6-3-LR/'},
			'CAM4-2degree':{'grid':'96x144','path':'/global/cscratch1/sd/pepflei/ETH/CAM4-2degree/'},
}

try:
	model=sys.argv[1]
	print model
	working_path=model_dict[model]['path']
	grid=model_dict[model]['grid']
except:
	model='ECHAM6-3-LR'
	working_path='data/tests/'

os.system('mkdir '+working_path+'/regional')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

for region in srex.keys():
	tmp={}
	for scenario in ['Plus20-Future','Plus15-Future','All-Hist']:
		data=da.read_nc(working_path+'/'+model+'_'+scenario+'_summerQ90.nc')
		tmp[scenario]={'90X_cum_heat':np.array([]),'90X_hot_shift':np.array([]),'90X_hot_temp':np.array([])}
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

	reg_dict={}
	for var in ['90X_cum_heat','90X_hot_shift','90X_hot_temp']:
		reg_dict[var]=da.DimArray(axes=[np.asarray(scenarios),np.array(range(len(tmp[scenario][var])))],dims=['scenario','ID'])
		for scenario in scenarios:
			reg_dict[var][scenario,:]=tmp[scenario][var]

	ds=da.Dataset(reg_dict)
	ds.write_nc(working_path+'/regional/'+region+'_'+model+'_summer.nc', mode='w')
