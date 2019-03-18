import os,sys,glob,time,collections,signal
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import subprocess as sub
import scipy.stats as stats

sys.path.append('/Users/peterpfleiderer/Projects/Persistence/persistence_in_models/')
import __settings
model_dict=__settings.model_dict


model='HadGHCND'
scenario='All-Hist'

os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
working_path='data/'+model+'/'


pers_file = working_path+scenario+'/HadGHCND_TMean_grided.1950-2014_period_warm.nc'
corWith_file = '../data/observations/GPCC_v7/full_data_v7_10_97x73_regrid_SPI3.nc'

data =da.read_nc(pers_file)
corWith_full = da.read_nc(corWith_file)['spi']
corWith_name = 'SPI3'

'''
carefully check time axis of both files
'''

pers_start = 1950
pers_end = 2014

corWith_start = 1901
corWith_end = 2013

index_shift = (pers_start - corWith_start) * 12
cut_start = corWith_start - pers_start
cut_end = (min(corWith_end,pers_end) - pers_start ) * 12

seasons={'MAM':0, 'JJA':1, 'SON':2, 'DJF':3}

if 'period_monthly_index' in data.keys():
	cor,cor_longest={},{}
	for stat in ['corrcoef','p_value']:
		cor[stat]=da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])
		cor_longest[stat]=da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])

	print('\n'+'\n10------50-------100')
	for y,progress in zip(data.lat,np.array([['-']+['']*(len(data.lat)/20+1)]*20).flatten()[0:len(data.lat)]):
		sys.stdout.write(progress); sys.stdout.flush()
		for x in data.lon:
			if np.sum(np.abs(data['period_length'][:,y,x]))!=0:
				pre_index=data['period_monthly_index'][:,y,x]

				avail_indices = np.where((pre_index>=cut_start) & (pre_index<=cut_end))[0]

				tmp_pers=data['period_length'][avail_indices,y,x].values
				tmp_time=data['period_midpoints'][avail_indices,y,x].values
				tmp_index=data['period_monthly_index'][avail_indices,y,x]
				tmp_corWith=corWith_full.ix[tmp_index+index_shift,:,:][:,y,x].values

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
	da.Dataset(cor).write_nc(working_path+scenario+'/cor_'+corWith_name+'_'+'_'.join([model,scenario])+'_warm.nc')
	cor_longest['corrcoef'].persistence = pers_file
	cor_longest['corrcoef'].correlated_with = corWith_file
	da.Dataset(cor_longest).write_nc(working_path+scenario+'/corLongest_'+corWith_name+'_'+'_'.join([model,scenario])+'_warm.nc')
