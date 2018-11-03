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
	os.chdir('/global/homes/p/pepflei/')


def get_regional_distribution(regions,model,style,add_name,states_to_analyze,scenarios=['All-Hist','Plus20-Future','Plus15-Future'],regions_id=''):
	region_dict={}
	for region in regions.keys():
		region_dict[region]={}
		for scenario in scenarios:
			pkl_file = open('data/'+model+'/'+style+'_'+model+'_'+scenario+'_'+add_name+'_counter.pkl', 'rb')
			distr_dict = pickle.load(pkl_file)	;	pkl_file.close()
			region_dict[region][scenario]={}
			tmp={}
			for season in ['MAM','JJA','SON','DJF']:
				print region,scenario,season
				region_dict[region][scenario][season]={}
				for state_name in states_to_analyze.values():
					region_dict[region][scenario][season][state_name]={}
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
							if len(distr_dict[str(y)+'_'+str(x)][season].keys())>=2:
								tmp[season]+=distr_dict[str(y)+'_'+str(x)][season]

			for season in ['MAM','JJA','SON','DJF']:
				if len(tmp[season])>=2:
					for state,state_name in states_to_analyze.items():
						count,pers=counter_to_pers(tmp[season],state)
						region_dict[region][scenario][season][state_name]['period_length']=pers
						region_dict[region][scenario][season][state_name]['count']=count
						region_dict[region][scenario][season]['counter']=tmp[season]

	output = open('data/'+model+'/'+style+'_'+add_name+'_'+model+'_regional_distrs_'+regions_id+'.pkl', 'wb')
	pickle.dump(region_dict, output)
	output.close()
	return region_dict


model=sys.argv[1]
print model

# region_dict=get_regional_distribution({'mid-lat':{'points':[(-180,-23),(180,-23),(180,-66),(-180,-66)]}},model,add_name='mid-lat-SH')


pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()
srex['mid-lat'] = {'points':[(-180,35),(180,35),(180,60),(-180,60)]}
#srex = {key:value for key,value in srex.items() if key in ['CEU','NEU','NAS','MED','WAS']}
region_dict=get_regional_distribution(regions=srex,model=model,style='pr',states_to_analyze={1:'5mm'},add_name='period5mm',scenarios=['All-Hist','Plus20-Future'],regions_id='srex')