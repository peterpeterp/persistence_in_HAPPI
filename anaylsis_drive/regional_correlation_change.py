import os,sys,glob,time,collections,signal
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import subprocess as sub
import scipy.stats as stats

try:
	model=sys.argv[1]
	region=sys.argv[2]
	print model,region

except:
	model = 'CAM4-2degree'
	region = 'CEU'

try:
	sys.path.append('/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/')
	os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter/')
	working_path='/p/tmp/pepflei/HAPPI/raw_data/reg_merge/'+model+'/'
	home_path = '/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/'
except:
	sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
	home_path = '/global/homes/p/pepflei/persistence_in_models/'

state_dict = {
	'warm':'tas',
	# 'dry':'pr',
	'5mm':'pr',
	# '10mm':'pr',
	'dry-warm':'cpd',
	}

seasons={'MAM':0, 'JJA':1, 'SON':2, 'DJF':3}


##############
# correaltions
##############

for scenario in ['All-Hist','Plus20-Future']:

	corWith_dict = {
		'SPI3':{
			'file':working_path+'/'+'_'.join(['SPI3',model,scenario,'bigMerge',region])+'.nc',
			'varname':'SPI3'
		},
		'EKE':{
			'file':working_path+'/'+'_'.join(['monEKE',model,scenario,'bigMerge',region])+'.nc',
			'varname':'eke'
		}
	}

	for corWith_name,details in corWith_dict.items():
		corWith_full = da.read_nc(details['file'])[details['varname']]
		corWith_run = da.read_nc(details['file'])['run_id']

		for state,style in state_dict.items():
			data = da.read_nc(working_path+'/'+'_'.join([style,model,scenario,'bigMerge',region,state])+'.nc')

			cor,cor_longest={},{}
			for stat in ['corrcoef','p_value']:
				cor[stat]=da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])
				cor_longest[stat]=da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])

			for y in data.lat:
				for x in data.lon:
					pers_loc=data['period_length'][:,y,x].values
					if pers_loc.sum() != 0:
						pers_loc=data['period_length'][:,y,x].values
						time_loc=data['period_midpoints'][:,y,x].values


						corWith_loc = np.array([])
						for run in range(100):
							tmp_index_loc_run = data['period_monthly_index'][:,y,x][data['run_id'][:,y,x]==run]
							tmp_corWith_loc_run = corWith_full[:,y,x][corWith_run[:,y,x]==run]
							corWith_loc = np.append(corWith_loc, tmp_corWith_loc_run.ix[tmp_index_loc_run,:,:])

							asdas

						# mask all
						mask = ~np.isnan(tmp_time) & ~np.isnan(tmp_pers) & ~np.isnan(tmp_corWith)
						tmp_time=tmp_time[mask]
						tmp_index = tmp_index[mask]
						tmp_pers=tmp_pers[mask]
						tmp_corWith=tmp_corWith[mask]
						tmp_sea=data['period_season'][avail_indices,y,x].values[mask]

						if tmp_pers.shape[0]>10:
							# detrend
							slope, intercept, r_value, p_value, std_err = stats.linregress(tmp_time,tmp_pers)
							pers=tmp_pers-(intercept+slope*tmp_time)+np.nanmean(tmp_pers)
							slope, intercept, r_value, p_value, std_err = stats.linregress(tmp_time,tmp_corWith)
							corWith=tmp_corWith-(intercept+slope*tmp_time)+np.nanmean(tmp_corWith)

							for season_name,season_id in seasons.items():
								cor['corrcoef'][season_name,y,x],cor['p_value'][season_name,y,x]=stats.pearsonr(pers[tmp_sea==season_id],corWith[tmp_sea==season_id])

							# longest period in month correlation
							sea_,pers_,corWith_,time_ = np.array([]),np.array([]),np.array([]),np.array([])
							for ind in sorted(set(tmp_index)):
								indices_of_mon = np.where(tmp_index==ind)[0]
								corWith_ = np.append(corWith_,tmp_corWith[indices_of_mon][0])
								pers_ = np.append(pers_,tmp_pers[indices_of_mon].max())
								sea_ = np.append(sea_,tmp_sea[indices_of_mon][0])
								time_ = np.append(time_,tmp_time[indices_of_mon][np.argmax(tmp_pers[indices_of_mon])])

							# detrend
							slope, intercept, r_value, p_value, std_err = stats.linregress(time_,pers_)
							pers=pers_-(intercept+slope*time_)+np.nanmean(pers_)
							slope, intercept, r_value, p_value, std_err = stats.linregress(time_,corWith_)
							corWith=corWith_-(intercept+slope*time_)+np.nanmean(corWith_)

							for season_name,season_id in seasons.items():
								cor_longest['corrcoef'][season_name,y,x],cor_longest['p_value'][season_name,y,x]=stats.pearsonr(pers[sea_==season_id],corWith[sea_==season_id])


		cor['corrcoef'].persistence = pers_file
		cor['corrcoef'].correlated_with = corWith_file
		da.Dataset(cor).write_nc(working_path+scenario+'/cor_'+corWith_name+'_'+'_'.join([model,scenario])+'_'+pers_name+'.nc')
		cor_longest['corrcoef'].persistence = pers_file
		cor_longest['corrcoef'].correlated_with = corWith_file
		da.Dataset(cor_longest).write_nc(working_path+scenario+'/corLongest_'+corWith_name+'_'+'_'.join([model,scenario])+'_'+pers_name+'.nc')
