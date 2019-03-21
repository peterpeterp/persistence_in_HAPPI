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
			'file':working_path+'/'+'_'.join(['SPI',model,scenario,'bigMerge',region])+'.nc',
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

			cor = {}
			for style in ['all','longest']:
				for stat in ['corrcoef','p-value']:
					cor[stat+'_'+style]=da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])

			for y in data.lat:
				for x in data.lon:
					pers_loc=data['period_length'][:,y,x].values
					if pers_loc.sum() != 0:
						run_loc = data['run_id'][:,y,x].values
						run_loc = run_loc[run_loc<100]
						pers_loc = data['period_length'][:,y,x].values[run_loc<100]
						time_loc = data['period_midpoints'][:,y,x].values[run_loc<100]
						monIndex_loc = data['period_monthly_index'][:,y,x].values[run_loc<100]

						corWith_loc = np.array([])
						for run in range(100):
							tmp_index_loc_run = monIndex_loc[run_loc==run]
							tmp_corWith_loc_run = corWith_full[:,y,x][corWith_run[:,y,x].values==run]
							corWith_loc = np.append(corWith_loc, tmp_corWith_loc_run.ix[tmp_index_loc_run])

						# mask all
						mask = ~np.isnan(pers_loc) & ~np.isnan(time_loc) & ~np.isnan(corWith_loc)
						time_loc=time_loc[mask]
						pers_loc=pers_loc[mask]
						monIndex_loc=monIndex_loc[mask]
						corWith_loc=corWith_loc[mask]
						sea_loc=data['period_season'][:,y,x].values[run_loc<100][mask]
						run_loc=run_loc[mask]

						# detrend
						slope, intercept, r_value, p_value, std_err = stats.linregress(time_loc,pers_loc)
						pers_loc_detrend=pers_loc-(intercept+slope*time_loc)+np.nanmean(pers_loc)
						slope, intercept, r_value, p_value, std_err = stats.linregress(time_loc,corWith_loc)
						corWith_loc_detrend=corWith_loc-(intercept+slope*time_loc)+np.nanmean(corWith_loc)

						for season_name,season_id in seasons.items():
							cor['corrcoef_all'][season_name,y,x],cor['p-value_all'][season_name,y,x]=stats.pearsonr(pers_loc_detrend[sea_loc==season_id],corWith_loc_detrend[sea_loc==season_id])

						# longest period in month correlation
						sea_,pers_,corWith_,time_ = np.array([]),np.array([]),np.array([]),np.array([])
						for run in range(100):
							tmp_index = monIndex_loc[run_loc==run]
							for ind in sorted(set(tmp_index)):
								indices_of_mon = np.where(tmp_index==ind)[0]
								corWith_ = np.append(corWith_,corWith_loc[indices_of_mon][0])
								pers_ = np.append(pers_,pers_loc[indices_of_mon].max())
								sea_ = np.append(sea_,sea_loc[indices_of_mon][0])
								time_ = np.append(time_,time_loc[indices_of_mon][np.argmax(pers_loc[indices_of_mon])])

						# detrend
						slope, intercept, r_value, p_value, std_err = stats.linregress(time_,pers_)
						pers=pers_-(intercept+slope*time_)+np.nanmean(pers_)
						slope, intercept, r_value, p_value, std_err = stats.linregress(time_,corWith_)
						corWith=corWith_-(intercept+slope*time_)+np.nanmean(corWith_)

						for season_name,season_id in seasons.items():
							cor['corrcoef_longest'][season_name,y,x],cor['p-value_longest'][season_name,y,x]=stats.pearsonr(pers[sea_==season_id],corWith[sea_==season_id])


		cor['corrcoef'].persistence = working_path+'/'+'_'.join([style,model,scenario,'bigMerge',region,state])+'.nc'
		cor['corrcoef'].correlated_with = details['file']
		da.Dataset(cor).write_nc(working_path.replace('reg_merge','reg_cor')+'/cor_'+corWith_name+'_'+'_'.join([model,scenario,region,state])+'.nc')
