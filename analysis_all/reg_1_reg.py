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

def counter_to_pers(counter,state=1):
	# to distribution
	pers_tmp=np.array(range(1,max([state*key+1 for key in counter.keys()])))
	count,pers=[],[]
	for pp,i in zip(pers_tmp,range(len(pers_tmp))):
		if pp*state in counter.keys():
			if abs(pp*state)!=0:
				count.append(counter[pp*state])
				pers.append(pp)
	count=np.array(count)
	pers=np.array(pers)
	return count,pers

def get_regional_distribution(regions,model,state_dict,scenarios=['All-Hist','Plus20-Future','Plus15-Future'],regions_id=''):
	region_dict={}
	for region in regions.keys():
		region_dict[region]={}
		for scenario in scenarios:
			region_dict[region][scenario]={}
			for state,style in state_dict.items():
				region_dict[region][scenario][state]={}
				pkl_file = open('data/'+model+'/'+style+'_'+model+'_'+scenario+'_'+state+'_counter.pkl', 'rb')
				distr_dict = pickle.load(pkl_file)	;	pkl_file.close()

				tmp={}
				for season in ['MAM','JJA','SON','DJF']:
					print region,scenario,season
					region_dict[region][scenario][state][season]={}
					tmp[season]=collections.Counter()

				if 'cells_in_region' not in region_dict[region]:
					region_dict[region]['cells_in_region'] = []
					polygon=Polygon(regions[region]['points'])
					for x in distr_dict['lon']:
						if x>180:
							x__=x-360
						else:
							x__=x
						for y in distr_dict['lat']:
							if polygon.contains(Point(x__,y)):
								region_dict[region]['cells_in_region'].append(str(y)+'_'+str(x))


				for cell in region_dict[region]['cells_in_region']:
					for season in ['MAM','JJA','SON','DJF']:
						if len(distr_dict[cell][season].keys())>=2:
							tmp[season]+=distr_dict[cell][season]

				for season in ['MAM','JJA','SON','DJF']:
					if len(tmp[season])>=2:
						count,pers=counter_to_pers(tmp[season])
						region_dict[region][scenario][state][season]['period_length']=pers
						region_dict[region][scenario][state][season]['count']=count
						region_dict[region][scenario][state][season]['counter']=tmp[season]

	output = open('data/'+model+'/'+model+'_regional_distrs_'+regions_id+'.pkl', 'wb')
	pickle.dump(region_dict, output)
	output.close()
	return region_dict


model=sys.argv[1]
print model

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()
srex['mid-lat'] = {'points':[(-180,35),(180,35),(180,60),(-180,60)]}
#srex = {key:value for key,value in srex.items() if key in ['CEU','NEU','NAS','MED','WAS']}
state_dict = {
	'warm':'tas',
	'dry':'pr',
	'5mm':'pr',
	'10mm':'pr',
	'dry-warm':'cpd',
	}
region_dict=get_regional_distribution(regions=srex,model=model,state_dict=state_dict,scenarios=['All-Hist','Plus20-Future','Plus15-Future'],regions_id='srex')



#
