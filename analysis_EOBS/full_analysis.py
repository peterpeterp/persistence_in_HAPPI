import os,sys,glob,time,collections,signal,gc
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import subprocess as sub
import scipy
from scipy import signal
from scipy import stats


def wait_timeout(proc, seconds):
	"""Wait for a process to finish, or raise exception after timeout"""
	start = time.time()
	end = start + seconds
	interval = min(seconds / 1000.0, .25)

	while True:
		result = proc.poll()
		if result is not None:
			return result
		if time.time() >= end:
			os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
			return 'failed'
		time.sleep(interval)


def try_several_times(command,trials=2,seconds=60):
	for trial in range(trials):
		proc=sub.Popen(command,stdout=sub.PIPE,shell=True, preexec_fn=os.setsid)
		result=wait_timeout(proc,seconds)
		if result!='failed':
			break
	return(result)


try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/p/projects/tumble/carls/shared_folder/Persistence/')

sys.path.append('weather_persistence/')
import persistence_functions as prsfc; reload(prsfc)

start_time=time.time()

#################
# temperature
#################
raw_file='data/EOBS/All-Hist/tg_0.50deg_reg_v17.0.nc'

result=try_several_times('cdo -O mergetime '+raw_file+' '+raw_file.replace('v17.0','2018')+' '+raw_file.replace('v17.0','merged'),1,120)
merged_file = raw_file.replace('v17.0','merged')

nc =  da.read_nc(merged_file)
tas = nc['tg']
tas_time = nc['time']
time_axis=np.array([dd.year + (dd.timetuple().tm_yday-1) / 365. for dd in num2date(tas_time,units = tas_time.units)])
month=np.array([dd.month for dd in num2date(tas_time,units = tas_time.units)])
yday=np.array([dd.timetuple().tm_yday for dd in num2date(tas_time,units = tas_time.units)])

anom = tas.copy() * np.nan
for y in tas.lat:
	print(y)
	for x in tas.lon:
		tmp__ = tas[:,y,x]
		notna = np.where(np.isfinite(tmp__))[0]
		if len(notna)>365*40:
			for day in range(1,367):
				days = np.where(yday[notna] == day)[0]
				tmp = tmp__.values[notna[days]]
				m, b, r_val, p_val, std_err = stats.linregress(time_axis[notna[days]],tmp)
				tmp = tmp - (time_axis[notna[days]]*m + b)
				tmp = tmp - np.nanmean(tmp)
				anom[:,y,x].ix[notna[days]] = tmp

anom_file = merged_file.replace('.nc','_anom.nc')
da.Dataset({'tg':anom,'time':nc['time'],'lat':nc['lat'],'lon':nc['lon']}).write_nc(anom_file)



# # state
tas_state_file=merged_file.replace('.nc','_state.nc')
prsfc.temp_anomaly_to_ind(anom_file,tas_state_file,var_name='tg')

#################
# Precipitation
#################
raw_file='data/EOBS/All-Hist/rr_0.50deg_reg_v17.0.nc'
result=try_several_times('cdo -O mergetime '+raw_file+' '+raw_file.replace('v17.0','2018')+' '+raw_file.replace('v17.0','merged'),1,120)
merged_file = raw_file.replace('v17.0','merged')

pr_state_file=merged_file.replace('.nc','_state.nc')
prsfc.precip_to_index(merged_file,pr_state_file,var_name='rr',unit_multiplier=1, states={'dry':{'mod':'below','threshold':1}, 'wet':{'mod':'above','threshold':1}, '5mm':{'mod':'above','threshold':5}, '10mm':{'mod':'above','threshold':10}})



#################
# Compound State
#################
compound_state_file=pr_state_file.replace('rr_0.50','cpd_0.50')
prsfc.compound_precip_temp_index(combinations={'dry-warm':[[pr_state_file,'dry'],[tas_state_file,'warm']]} ,out_file=compound_state_file)
gc.collect()

#################
# Persistence
#################
prsfc.get_persistence(tas_state_file,states_to_analyze=['warm'],lat_name='latitude',lon_name='longitude')
prsfc.get_persistence(pr_state_file,states_to_analyze=['dry','10mm','5mm'],lat_name='latitude',lon_name='longitude')
prsfc.get_persistence(compound_state_file,states_to_analyze=['dry-warm'],lat_name='latitude',lon_name='longitude')

#################
# Bring it into the right format
#################

import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import dimarray as da
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

model='EOBS'

overwrite=True

working_path='data/EOBS/'

seasons={'MAM':{'months':[3,4,5],'index':0}, 'JJA':{'months':[6,7,8],'index':1}, 'SON':{'months':[9,10,11],'index':2}, 'DJF':{'months':[12,1,2],'index':3}}

state_dict = {
	'warm':'tg',
	'dry':'rr',
	'5mm':'rr',
	'10mm':'rr',
	'dry-warm':'cpd',
	}

for state,style in state_dict.items():
	for scenario in ['All-Hist']:
		all_files=sorted(glob.glob(working_path+scenario+'/'+style+'*merged*'+state+'.nc'))
		print all_files

		nc_in=Dataset(all_files[0],'r')
		lat=nc_in.variables['latitude'][:]
		lon=nc_in.variables['longitude'][:]
		nc_in.close()

		distr_dict={}
		for y in lat:
			for x in lon:
				distr_dict[str(y)+'_'+str(x)]={'MAM':collections.Counter(),'JJA':collections.Counter(),'SON':collections.Counter(),'DJF':collections.Counter()}

		for file in all_files:
			start_time=time.time()
			print file
			nc_in=Dataset(file,'r')
			try:
				period_length=nc_in.variables['period_length'][:,:,:]
				period_season=nc_in.variables['period_season'][:,:,:]

				for iy in range(len(lat)):
					sys.stdout.write('.')	;	sys.stdout.flush()
					for ix in range(len(lon)):
						for season in seasons.keys():
							in_season=np.where(period_season[:,iy,ix]==seasons[season]['index'])[0]
							distr_dict[str(lat[iy])+'_'+str(lon[ix])][season]+=collections.Counter(period_length[:,iy,ix][in_season])
			except:
				failed_files=open(working_path+scenario+'/damaged_files.txt','w')
				failed_files.write(file+'\n')
				failed_files.close()

			print time.time()-start_time

		distr_dict['lon']=lon
		distr_dict['lat']=lat

		output = open('data/'+model+'/'+style+'_'+model+'_'+scenario+'_'+state+'_counter.pkl', 'wb')
		pickle.dump(distr_dict, output)
		output.close()


# regional
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
				pkl_file = open('data/'+model+'/'+style_dict[style]+'_'+model+'_'+scenario+'_'+state+'_counter.pkl', 'rb')
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


model='EOBS'
print model



pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()
srex['mid-lat'] = {'points':[(-180,35),(180,35),(180,60),(-180,60)]}
#srex = {key:value for key,value in srex.items() if key in ['CEU','NEU','NAS','MED','WAS']}

style_dict = {
	'tas':'tg',
	'pr':'rr',
	'cpd':'cpd'
}

state_dict = {
	'warm':'tas',
	'dry':'pr',
	'5mm':'pr',
	'10mm':'pr',
	'dry-warm':'cpd',
	}
region_dict=get_regional_distribution(regions=srex,model=model,state_dict=state_dict,scenarios=['All-Hist'],regions_id='srex')


# mean qu

def counter_to_list(counter):
	tmp=[]
	lengths=counter.keys()
	if 0 in lengths:
		lengths.remove(0)
	if len(lengths)>2:
		for key in lengths:
			for i in range(counter[key]):
				tmp.append(key)
		tmp=np.array(tmp)
		return -tmp[tmp<0],tmp[tmp>0]
	else:
		return [],[]

def quantile_from_cdf(x,qu):
	counts, bin_edges = np.histogram(x, bins=range(0,max(x)+1), normed=True)
	cdf = np.cumsum(counts)

	quantiles=[]
	for q in qu:
		if q>=1:q/=100.
		x1=np.where(cdf<q)[0][-1]
		quantiles.append(x1+(q-cdf[x1])/(cdf[x1+1]-cdf[x1]))

	return quantiles

model='EOBS'

overwrite=True

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

working_path='data/EOBS/'

scenarios=['All-Hist']
seasons=['MAM','JJA','SON','DJF','year']

types=['mean','qu_1','qu_5','qu_10','qu_25','qu_50','qu_75','qu_90','qu_95','qu_99','npqu_1','npqu_5','npqu_10','npqu_25','npqu_50','npqu_75','npqu_90','npqu_95','npqu_99']

state_dict = {
	'warm':'tg',
	'dry':'rr',
	'5mm':'rr',
	'10mm':'rr',
	'dry-warm':'cpd',
	}

for state,style in state_dict.items():

	big_dict={}
	for scenario in scenarios:
		pkl_file = open('data/'+model+'/'+style+'_'+model+'_'+scenario+'_'+state+'_counter.pkl', 'rb')
		big_dict[scenario] = pickle.load(pkl_file)	;	pkl_file.close()

	lat=np.ma.getdata(big_dict[scenario]['lat'])
	lon=np.ma.getdata(big_dict[scenario]['lon'])

	if 'SummaryMeanQu' not in globals():
		SummaryMeanQu=da.DimArray(axes=[np.asarray(scenarios),np.asarray(seasons),np.asarray(state_dict.keys()),np.asarray(types),lat,lon], dims=['scenario','season','state','type','lat','lon'])

	for scenario in scenarios:
		distr_dict = big_dict[scenario]

		for iy in range(len(lat)):
			for ix in range(len(lon)):
				grid_cell=distr_dict[str(lat[iy])+'_'+str(lon[ix])]
				grid_cell['year']=grid_cell['MAM']+grid_cell['JJA']+grid_cell['SON']+grid_cell['DJF']

		for season in seasons:
			print season
			for iy in range(len(lat)):
				sys.stdout.write('.')	;	sys.stdout.flush()
				for ix in range(len(lon)):
					counter=distr_dict[str(lat[iy])+'_'+str(lon[ix])][season]
					if len(counter)>3:
						neg,pos=counter_to_list(counter)
						SummaryMeanQu[scenario,season,state,'mean',lat[iy],lon[ix]]=np.mean(pos)
							#SummaryMeanQu[scenario][season][state_name].ix[1:10,iy,ix]=np.percentile(distr,[1.,5.,10.,25.,50.,75.,90.,95.,99.])
						try:
							SummaryMeanQu[scenario,season,state,['qu_1','qu_5','qu_10','qu_25','qu_50','qu_75','qu_90','qu_95','qu_99'],lat[iy],lon[ix]]=quantile_from_cdf(pos,[1.,5.,10.,25.,50.,75.,90.,95.,99.])
						except:
							pass
						SummaryMeanQu[scenario,season,state,['npqu_1','npqu_5','npqu_10','npqu_25','npqu_50','npqu_75','npqu_90','npqu_95','npqu_99'],lat[iy],lon[ix]]=np.nanpercentile(pos,[1.,5.,10.,25.,50.,75.,90.,95.,99.])

ds=da.Dataset({'SummaryMeanQu':SummaryMeanQu})
ds.write_nc('data/'+model+'/'+model+'_SummaryMeanQu.nc', mode='w')
