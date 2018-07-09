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

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei)

def get_regional_distribution(regions,model,scenarios=['All-Hist','1954-1974','1990-2010'],add_name=''):
	region_dict={}
	for region in regions.keys():
		print(region)
		region_dict[region]={}
		for scenario in scenarios:
			pkl_file = open('data/'+model+'/'+model+'_'+scenario+'_counter.pkl', 'rb')
			distr_dict = pickle.load(pkl_file)	;	pkl_file.close()
			region_dict[region][scenario]={}
			tmp={}
			for season in ['MAM','JJA','SON','DJF']:
				region_dict[region][scenario][season]={'cold':{},'warm':{}}
				tmp[season]=collections.Counter()
			polygon=Polygon(regions[region]['points'])
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

	output = open('data/'+model+'/'+model+'_regional_distrs_'+add_name+'.pkl', 'wb')
	pickle.dump(region_dict, output)
	output.close()
	return region_dict

model='HadGHCND'
# wave_polys={'7_1':{'points':[(-180,23),(180,23),(180,66),(-180,66)]},
# 				{'points':[(-180,23),(180,23),(180,66),(-180,66)]},
# 				{'points':[(-180,23),(180,23),(180,66),(-180,66)]},
# 				{'points':[(-180,23),(180,23),(180,66),(-180,66)]},
# 				{'points':[(-180,23),(180,23),(180,66),(-180,66)]},
# 				{'points':[(-180,23),(180,23),(180,66),(-180,66)]}}
# region_dict=get_regional_distribution(wave_polys,model,add_name='mid-lat')

region_dict=get_regional_distribution({'mid-lat':{'points':[(-180,-23),(180,-23),(180,-66),(-180,-66)]}},model,add_name='mid-lat-SH')

region_dict=get_regional_distribution({'mid-lat':{'points':[(-180,35),(180,35),(180,60),(-180,60)]}},model,add_name='mid-lat')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()
region_dict=get_regional_distribution(srex,model,add_name='srex')
