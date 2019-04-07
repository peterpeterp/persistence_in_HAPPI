import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import dimarray as da
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

model=sys.argv[1]
print model
#chosen_scenario=sys.argv[2]

os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter/')

overwrite=True

working_path='/p/tmp/pepflei/HAPPI/raw_data/'+model+'/'
scenarios=['Plus20-Artificial-v1']


seasons={'MAM':{'months':[3,4,5],'index':0}, 'JJA':{'months':[6,7,8],'index':1}, 'SON':{'months':[9,10,11],'index':2}, 'DJF':{'months':[12,1,2],'index':3}}

state_dict = {
	'dry':'pr',
	'5mm':'pr',
	}
#
# for state,style in state_dict.items():
# 	for scenario in scenarios:	#,'Plus15-Future','Plus20-Future'
# 		#if scenario==chosen_scenario:
# 		all_files=sorted(glob.glob(working_path+scenario+'/'+style+'/'+style+'*'+state+'.nc'))
# 		print all_files
#
# 		nc_in=Dataset(all_files[0],'r')
# 		lat=nc_in.variables['lat'][:]
# 		lon=nc_in.variables['lon'][:]
# 		nc_in.close()
#
# 		distr_dict={}
# 		for y in lat:
# 			for x in lon:
# 				distr_dict[str(y)+'_'+str(x)]={'MAM':collections.Counter(),'JJA':collections.Counter(),'SON':collections.Counter(),'DJF':collections.Counter()}
#
# 		for file in all_files:
# 			start_time=time.time()
# 			print file
# 			nc_in=Dataset(file,'r')
# 			try:
# 				period_length=nc_in.variables['period_length'][:,:,:]
# 				period_season=nc_in.variables['period_season'][:,:,:]
#
# 				for iy in range(len(lat)):
# 					sys.stdout.write('.')	;	sys.stdout.flush()
# 					for ix in range(len(lon)):
# 						for season in seasons.keys():
# 							in_season=np.where(period_season[:,iy,ix]==seasons[season]['index'])[0]
# 							distr_dict[str(lat[iy])+'_'+str(lon[ix])][season]+=collections.Counter(period_length[:,iy,ix][in_season])
# 			except:
# 				failed_files=open(working_path+scenario+'/damaged_files.txt','w')
# 				failed_files.write(file+'\n')
# 				failed_files.close()
#
# 			print time.time()-start_time
#
# 		distr_dict['lon']=lon
# 		distr_dict['lat']=lat
#
# 		output = open('data/'+model+'/'+style+'_'+model+'_'+scenario+'_'+state+'_counter.pkl', 'wb')
# 		pickle.dump(distr_dict, output)
# 		output.close()
#
##################
# regional distrs
##################

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

def get_regional_distribution(regions,model,state_dict,scenarios=scenarios,regions_id=''):
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

	output = open('data/'+model+'/'+model+'_regional_distrs_'+regions_id+'_artificial.pkl', 'wb')
	pickle.dump(region_dict, output)
	output.close()
	return region_dict

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()
srex['mid-lat'] = {'points':[(-180,35),(180,35),(180,60),(-180,60)]}
srex = {key:value for key,value in srex.items() if key in ['EAS','TIB','CAS','WAS','MED','CEU','NEU','NAS','ENA','CNA','WNA','CGI','ALA']}
state_dict = {
	'dry':'pr',
	'5mm':'pr',
	}
region_dict=get_regional_distribution(regions=srex,model=model,state_dict=state_dict,scenarios=scenarios,regions_id='srex')



##################
# BIg summary
##################
#
#
# def counter_to_list(counter):
# 	tmp=[]
# 	lengths=counter.keys()
# 	if 0 in lengths:
# 		lengths.remove(0)
# 	if len(lengths)>2:
# 		for key in lengths:
# 			for i in range(counter[key]):
# 				tmp.append(key)
# 		tmp=np.array(tmp)
# 		return -tmp[tmp<0],tmp[tmp>0]
# 	else:
# 		return [],[]
#
# def quantile_from_cdf(x,qu):
# 	counts, bin_edges = np.histogram(x, bins=range(0,max(x)+1), normed=True)
# 	cdf = np.cumsum(counts)
#
# 	quantiles=[]
# 	for q in qu:
# 		if q>=1:q/=100.
# 		x1=np.where(cdf<q)[0][-1]
# 		quantiles.append(x1+(q-cdf[x1])/(cdf[x1+1]-cdf[x1]))
#
# 	return quantiles
#
# types=['mean','qu_1','qu_5','qu_10','qu_25','qu_50','qu_75','qu_90','qu_95','qu_99','npqu_1','npqu_5','npqu_10','npqu_25','npqu_50','npqu_75','npqu_90','npqu_95','npqu_99']
# seasons=['MAM','JJA','SON','DJF']
#
# for state,style in state_dict.items():
# 	big_dict={}
# 	for scenario in scenarios:
# 		pkl_file = open('data/'+model+'/'+style+'_'+model+'_'+scenario+'_'+state+'_counter.pkl', 'rb')
# 		big_dict[scenario] = pickle.load(pkl_file)	;	pkl_file.close()
#
# 	lat=big_dict[scenario]['lat']
# 	lon=big_dict[scenario]['lon']
#
# 	if 'SummaryMeanQu' not in globals():
# 		SummaryMeanQu=da.DimArray(axes=[np.asarray(scenarios),np.asarray(seasons),np.asarray(state_dict.keys()),np.asarray(types),lat,lon], dims=['scenario','season','state','type','lat','lon'])
#
# 	for scenario in scenarios:
# 		distr_dict = big_dict[scenario]
#
# 		for iy in range(len(lat)):
# 			for ix in range(len(lon)):
# 				grid_cell=distr_dict[str(lat[iy])+'_'+str(lon[ix])]
# 				grid_cell['year']=grid_cell['MAM']+grid_cell['JJA']+grid_cell['SON']+grid_cell['DJF']
#
# 		for season in seasons:
# 			print season
# 			for iy in range(len(lat)):
# 				sys.stdout.write('.')	;	sys.stdout.flush()
# 				for ix in range(len(lon)):
# 					counter=distr_dict[str(lat[iy])+'_'+str(lon[ix])][season]
# 					if len(counter)>3:
# 						neg,pos=counter_to_list(counter)
# 						SummaryMeanQu[scenario,season,state,'mean',lat[iy],lon[ix]]=np.mean(pos)
# 							#SummaryMeanQu[scenario][season][state_name].ix[1:10,iy,ix]=np.percentile(distr,[1.,5.,10.,25.,50.,75.,90.,95.,99.])
# 						try:
# 							SummaryMeanQu[scenario,season,state,['qu_1','qu_5','qu_10','qu_25','qu_50','qu_75','qu_90','qu_95','qu_99'],lat[iy],lon[ix]]=quantile_from_cdf(pos,[1.,5.,10.,25.,50.,75.,90.,95.,99.])
# 						except:
# 							pass
# 						SummaryMeanQu[scenario,season,state,['npqu_1','npqu_5','npqu_10','npqu_25','npqu_50','npqu_75','npqu_90','npqu_95','npqu_99'],lat[iy],lon[ix]]=np.nanpercentile(pos,[1.,5.,10.,25.,50.,75.,90.,95.,99.])
#
# ds=da.Dataset({'SummaryMeanQu':SummaryMeanQu})
# ds.write_nc('data/'+model+'/'+model+'_SummaryMeanQu_arificial.nc', mode='w')
#
#
#
#
# #
