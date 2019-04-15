import os,sys,glob,time,collections,signal,gc
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
	'dry':'pr',
	'5mm':'pr',
	'dry-warm':'cpd',
	}

seasons={'MAM':0, 'JJA':1, 'SON':2, 'DJF':3}
season_indices_monthly = {}
for season_name,months in {'MAM':[2,3,4], 'JJA':[5,6,7], 'SON':[8,9,10], 'DJF':[11,0,1]}.items():
	tmp = np.zeros([12000],np.bool)
	for mon in months:
		tmp[mon::12] = 1
	season_indices_monthly[season_name] = tmp



import __settings
model_dict=__settings.model_dict
reg_mask = da.read_nc('masks/srex_mask_'+model_dict[model]['grid']+'.nc')[region][0:,:]
reg_mask.lat = np.round(reg_mask.lat,02)
reg_mask.lon = np.round(reg_mask.lon,02)


##############
# correaltions
##############

for scenario in ['All-Hist','Plus20-Future']:
	print('__________'+scenario)

	nc = da.read_nc(glob.glob('/p/tmp/pepflei/HAPPI/raw_data/'+model+'/'+scenario+'/pr/*state.nc')[0])
	units = nc['time'].units
	calendar = nc['time'].calendar

	corWith_dict = {
		'SPI3':{
			'file':working_path+'/'+'_'.join(['SPI',model,scenario,'bigMerge',region])+'.nc',
			'varname':'SPI3'
		},
		'EKE':{
			'file':working_path+'/'+'_'.join(['EKE',model,scenario,'bigMerge',region])+'.nc',
			'varname':'eke'
		}
	}

	for corWith_name,details in corWith_dict.items():
		print('*******************'+corWith_name)
		nc_corWith = da.read_nc(details['file'])
		nc_corWith.lat = np.round(nc_corWith.lat,02)
		nc_corWith.lon = np.round(nc_corWith.lon,02)
		corWith_full = nc_corWith[details['varname']]
		corWith_run = nc_corWith['run_id']

		# print(np.nanpercentile(corWith_full,range(101)))

		for state,style in state_dict.items():
			print('----------------------------'+state)
			data = da.read_nc(working_path+'/'+'_'.join([style,model,scenario,'bigMerge',region,state])+'.nc')
			data.lat = np.round(data.lat,02)
			data.lon = np.round(data.lon,02)

			cor = {}
			for style in ['','_lagged','_season','_lagged_season']:
				for stat in ['corrcoef','p-value']:
					cor[stat+style]=da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])
			for stat in ['lr_intercept','lr_slope','lr_pvalue']:
				cor[stat]=da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])

			statistics = {}
			for xxx in [corWith_name,state]:
				for stat in ['mean','10','25','33','50','66','75','90','100']:
					statistics[stat+'_'+xxx]=da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])
			statistics['mean_of_10percLongest_'+state] = da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])
			statistics['mean_of_10percLongest_'+corWith_name] =  da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])
			statistics['mean_of_10percLongest_lagged_'+corWith_name] =  da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])


			for y in data.lat:
				for x in data.lon:
					pers_loc=data['period_length'][:,y,x].values
					# print(np.nanpercentile(pers_loc,range(101)))
					if pers_loc.sum() != 0 and reg_mask[y,x] != 0:
						print(y,x)

						################
						# mean of corwith
						################
						for season_name,indices in season_indices_monthly.items():
							statistics['mean_'+corWith_name][season_name,y,x] = np.nanmean(corWith_full[:,y,x].values[indices])
							for qu in [10,25,33,50,66,75,90,100]:
								statistics[str(qu)+'_'+corWith_name][season_name,y,x] = np.nanpercentile(corWith_full[:,y,x].values[indices],qu)

						# print(np.nanmean(corWith_full[:,y,x].values[indices]))
						run_loc = data['run_id'][:,y,x].values
						valid_runs = run_loc < 100
						run_loc = run_loc[valid_runs]
						pers_loc = data['period_length'][:,y,x].values[valid_runs]
						time_loc = data['period_midpoints'][:,y,x].values[valid_runs]
						monIndex_loc = data['period_monthly_index'][:,y,x].values[valid_runs]

						corWith_loc = np.array([])
						corWith_loc_lagged = np.array([])
						for run in range(100):
							tmp_index_loc_run = monIndex_loc[run_loc==run]
							tmp_corWith_loc_run = corWith_full[:,y,x][corWith_run[:,y,x].values==run]
							corWith_loc = np.append(corWith_loc, tmp_corWith_loc_run.ix[tmp_index_loc_run])
							# month before
							tmp_index_loc_run_lagged = monIndex_loc[run_loc==run] -1
							issue_months = np.where(tmp_index_loc_run_lagged < 0)[0]
							tmp_index_loc_run_lagged[issue_months] = 0
							tmp_tmp = tmp_corWith_loc_run.ix[tmp_index_loc_run_lagged]
							tmp_tmp.ix[issue_months] = np.nan
							corWith_loc_lagged = np.append(corWith_loc_lagged, tmp_tmp)

						# mask all
						mask = ~np.isnan(pers_loc) & ~np.isnan(time_loc) & ~np.isnan(corWith_loc) & ~np.isnan(corWith_loc_lagged)
						time_loc=time_loc[mask]
						year_loc =  np.array([date.year for date in num2date(time_loc, units = units, calendar=calendar)])
						pers_loc=pers_loc[mask]
						monIndex_loc=monIndex_loc[mask]
						corWith_loc=corWith_loc[mask]
						corWith_loc_lagged=corWith_loc_lagged[mask]
						sea_loc=data['period_season'][:,y,x].values[valid_runs][mask]
						run_loc=run_loc[mask]

						for season_name,season_id in seasons.items():
							valid_season = sea_loc==season_id
							pers_loc_sea = pers_loc[valid_season]
							if pers_loc_sea.shape[0]>10:
								time_loc_sea = time_loc[valid_season]
								year_loc_sea = year_loc[valid_season]
								monIndex_loc_sea = monIndex_loc[valid_season]
								run_loc_sea = run_loc[valid_season]
								corWith_loc_sea = corWith_loc[valid_season]
								corWith_loc_lagged_sea = corWith_loc_lagged[valid_season]

								################
								# mean
								################
								statistics['mean_'+state][season_name,y,x] = np.nanmean(pers_loc_sea)
								for qu in [10,25,33,50,66,75,90,100]:
									statistics[str(qu)+'_'+state][season_name,y,x] = np.nanpercentile(pers_loc_sea,qu)

								'''
								detrend and normalize
								detrending might be stupid in 10 year runs

								mean eke/spi of 10% longest events

								spi before event
								'''

								# # detrend
								# slope, intercept, r_value, p_value, std_err = stats.linregress(time_loc_sea,pers_loc_sea)
								# pers_loc_sea_detrend = pers_loc_sea-(intercept+slope*time_loc_sea)
								# slope, intercept, r_value, p_value, std_err = stats.linregress(time_loc_sea,corWith_loc_sea)
								# corWith_loc_sea_detrend = corWith_loc_sea-(intercept+slope*time_loc_sea)
								# slope, intercept, r_value, p_value, std_err = stats.linregress(time_loc_sea,corWith_loc_lagged_sea)
								# corWith_loc_lagged_sea_detrend = corWith_loc_lagged_sea-(intercept+slope*time_loc_sea)

								# normalize
								pers_loc_sea_norm = (pers_loc_sea - pers_loc_sea.max()) / (pers_loc_sea.min() - pers_loc_sea.max())
								corWith_loc_sea_norm = (corWith_loc_sea - corWith_loc_sea.max()) / (corWith_loc_sea.min() - corWith_loc_sea.max())
								corWith_loc_lagged_sea_norm = (corWith_loc_lagged_sea - corWith_loc_lagged_sea.max()) / (corWith_loc_lagged_sea.min() - corWith_loc_lagged_sea.max())

								################
								# correlation
								################
								cor['corrcoef'][season_name,y,x],cor['p-value'][season_name,y,x] = stats.pearsonr(pers_loc_sea_norm,corWith_loc_sea_norm)
								cor['corrcoef_lagged'][season_name,y,x],cor['p-value_lagged'][season_name,y,x] = stats.pearsonr(pers_loc_sea_norm,corWith_loc_lagged_sea_norm)

								################
								# regression
								################
								slope, intercept, r_value, p_value, std_err = stats.linregress(pers_loc_sea_norm,corWith_loc_sea_norm)
								cor['lr_slope'][season_name,y,x] = slope
								cor['lr_intercept'][season_name,y,x] = intercept
								cor['lr_pvalue'][season_name,y,x] = p_value

								###################
								# longest in season
								###################
								pers_loc_sea_, corWith_loc_sea_, corWith_loc_sea_lagged_ = np.array([]), np.array([]), np.array([])
								for run in range(100):
									tmp_year = year_loc_sea[run_loc_sea==run]
									for yr in sorted(set(tmp_year)):
										indices_of_year = np.where(tmp_year==yr)[0]
										corWith_loc_sea_ = np.append(corWith_loc_sea_,corWith_loc_sea_norm[indices_of_year][0])
										corWith_loc_sea_lagged_ = np.append(corWith_loc_sea_lagged_,corWith_loc_lagged_sea_norm[indices_of_year][0])
										pers_loc_sea_ = np.append(pers_loc_sea_,pers_loc_sea_norm[indices_of_year].max())

								cor['corrcoef_season'][season_name,y,x],cor['p-value_season'][season_name,y,x] = stats.pearsonr(pers_loc_sea_,corWith_loc_sea_)
								cor['corrcoef_lagged_season'][season_name,y,x],cor['p-value_lagged_season'][season_name,y,x] = stats.pearsonr(pers_loc_sea_,corWith_loc_sea_lagged_)


								###################
								# longest in events
								###################
								longest_events = np.argwhere(pers_loc_sea >= np.percentile(pers_loc_sea,90))
								statistics['mean_of_10percLongest_'+state][season_name,y,x] = np.nanmean(pers_loc_sea[longest_events])
								statistics['mean_of_10percLongest_'+corWith_name][season_name,y,x] = np.nanmean(corWith_loc_sea[longest_events])
								statistics['mean_of_10percLongest_lagged_'+corWith_name][season_name,y,x] = np.nanmean(corWith_loc_lagged_sea[longest_events])


								# ################
								# # detrend longest in month
								# ################
								#
								# pers_loc_sea_, corWith_loc_sea_ = np.array([]), np.array([])
								# for run in range(100):
								# 	pers_,corWith_,time_ = np.array([]),np.array([]),np.array([])
								# 	tmp_index = monIndex_loc_sea[run_loc_sea==run]
								# 	for ind in sorted(set(tmp_index)):
								# 		indices_of_mon = np.where(tmp_index==ind)[0]
								# 		corWith_loc_sea_ = np.append(corWith_loc_sea_,corWith_loc_sea[indices_of_mon][0])
								# 		pers_loc_sea_ = np.append(pers_loc_sea_,pers_loc_sea[indices_of_mon].max())
								# 		time_ = np.append(time_,time_loc_sea[indices_of_mon][np.argmax(pers_loc_sea[indices_of_mon])])
								#
								# 	'''
								# 	slope, intercept, r_value, p_value, std_err = stats.linregress(time_,pers_)
								# 	pers_loc_sea_detrend = np.append(pers_loc_sea_detrend, pers_-(intercept+slope*time_)+np.nanmean(pers_))
								# 	slope, intercept, r_value, p_value, std_err = stats.linregress(time_,corWith_)
								# 	corWith_loc_sea_detrend = np.append(corWith_loc_sea_detrend, corWith_-(intercept+slope*time_)+np.nanmean(corWith_))
								# 	'''

								################
								# correlation longest
								################
								#
								# cor['corrcoef_longest'][season_name,y,x],cor['p-value_longest'][season_name,y,x]=stats.pearsonr(pers_loc_sea_,corWith_loc_sea_)
								#

								gc.collect()

			ds = da.Dataset(cor)
			ds.persistence = working_path+'/'+'_'.join([style,model,scenario,'bigMerge',region,state])+'.nc'
			ds.correlated_with = details['file']
			ds.write_nc(working_path.replace('reg_merge','reg_cor')+'/cor_'+corWith_name+'_'+'_'.join([model,scenario,region,state])+'.nc')

			da.Dataset(statistics).write_nc(working_path.replace('reg_merge','reg_stats')+'/stats_'+corWith_name+'_'+'_'.join([model,scenario,region,state])+'.nc')

'''

EAS TIB CAS WAS MED CEU ENA CNA WNA NAS NEU CGI ALA NHml

'''
