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

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

def get_regional_distribution(model,scenarios=['Plus20-Future','Plus15-Future','All-Hist']):
	region_dict={}
	for region in srex.keys():
		region_dict[region]={}
		for scenario in scenarios:
			pkl_file = open('data/'+model+'_'+scenario+'_counter.pkl', 'rb')
			distr_dict = pickle.load(pkl_file)	;	pkl_file.close()
			region_dict[region][scenario]={}
			tmp={}
			for season in ['MAM','JJA','SON','DJF']:
				print region,scenario,season
				region_dict[region][scenario][season]={'cold':{},'warm':{}}
				tmp[season]=collections.Counter()
			polygon=Polygon(srex[region]['points'])
			for x in distr_dict['lon']:
				if x>180:
					x__=x-360
				else:
					x__=x
				for y in distr_dict['lat']:
					if polygon.contains(Point(x__,y)):
						for season in ['MAM','JJA','SON','DJF']:
							if len(distr_dict[str(y)+'_'+str(x)][season].keys())>10:
								tmp[season]+=distr_dict[str(y)+'_'+str(x)][season]

			for season in ['MAM','JJA','SON','DJF']:
				if len(tmp[season])>5:
					for state,state_name in zip([-1,1],['cold','warm']):
						count,pers=counter_to_pers(tmp[season],state)
						region_dict[region][scenario][season][state_name]['period_length']=pers
						region_dict[region][scenario][season][state_name]['count']=count
						region_dict[region][scenario][season]['counter']=tmp[season]

	output = open('data/'+model+'_regional_distrs.pkl', 'wb')
	pickle.dump(region_dict, output)
	output.close()
	return region_dict

#region_dict=get_regional_distribution('CAM4')

def get_regional_summer_stats(model,scenarios=['Plus20-Future','Plus15-Future','All-Hist']):
	for region in srex.keys():
		tmp={}
		for scenario in scenarios:
			data=da.read_nc('data/'+model+'_'+scenario+'_SummerStats.nc')
			tmp[scenario]={'stat_Xpers_cum_heat':np.array([]),'stat_Xpers_hot_shift':np.array([]),'stat_Xpers_hot_temp':np.array([]),'stat_tasX_pers_rank':np.array([])}
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
		for var in ['stat_Xpers_cum_heat','stat_Xpers_hot_shift','stat_Xpers_hot_temp','stat_tasX_pers_rank']:
			reg_dict[var]=da.DimArray(axes=[np.asarray(scenarios),np.array(range(len(tmp[scenario][var])))],dims=['scenario','ID'])
			for scenario in scenarios:
				reg_dict[var][scenario,:]=tmp[scenario][var]

		ds=da.Dataset(reg_dict)
		ds.write_nc('data/region/'+region+'_'+model+'_summer.nc', mode='w')

stat_dict=get_regional_summer_stats('ECHAM6-3-LR')
