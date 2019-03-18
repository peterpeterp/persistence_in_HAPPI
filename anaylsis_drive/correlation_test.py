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
eke_file = 'data/EKE/ERA-Interim_EKE_1979-2015_500mbar_mon.nc'

# data=da.read_nc(pers_file)
# EKE=da.read_nc(eke_file)['EKE']

seasons={'MAM':0, 'JJA':1, 'SON':2, 'DJF':3}

if 'period_monthly_index' in data.keys():
	cor_eke,cor_eke_longest={},{}
	for stat in ['corrcoef','p_value']:
		cor_eke[stat]=da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])
		cor_eke_longest[stat]=da.DimArray(axes=[seasons.keys(),data.lat,data.lon],dims=['season','lat','lon'])

	print('\n'+run+'\n10------50-------100')
	for y,progress in zip(data.lat,np.array([['-']+['']*(len(data.lat)/20+1)]*20).flatten()[0:len(data.lat)]):
		sys.stdout.write(progress); sys.stdout.flush()
		for x in data.lon:
			if np.sum(np.abs(data['period_length'][:,y,x]))!=0:
				pre_index=data['period_monthly_index'][:,y,x]

				avail_indices = np.where(pre_index>=348)[0]

				tmp_pers=data['period_length'][avail_indices,y,x].values
				tmp_time=data['period_midpoints'][avail_indices,y,x].values
				tmp_index=data['period_monthly_index'][avail_indices,y,x]
				tmp_eke=EKE.ix[tmp_index-348,:,:][:,y,x].values

				# mask all
				mask = ~np.isnan(tmp_time) & ~np.isnan(tmp_pers) & ~np.isnan(tmp_eke)
				tmp_time=tmp_time[mask]
				tmp_index = tmp_index[mask]
				tmp_pers=tmp_pers[mask]
				tmp_eke=tmp_eke[mask]
				tmp_sea=data['period_season'][avail_indices,y,x].values[mask]

				if tmp_pers.shape[0]>10:
					# detrend
					slope, intercept, r_value, p_value, std_err = stats.linregress(tmp_time,tmp_pers)
					pers=tmp_pers-(intercept+slope*tmp_time)+np.nanmean(tmp_pers)
					slope, intercept, r_value, p_value, std_err = stats.linregress(tmp_time,tmp_eke)
					eke=tmp_eke-(intercept+slope*tmp_time)+np.nanmean(tmp_eke)

					for season_name,season_id in seasons.items():
						cor_eke['corrcoef'][season_name,y,x],cor_eke['p_value'][season_name,y,x]=stats.pearsonr(pers[tmp_sea==season_id],eke[tmp_sea==season_id])

					# longest period in month correlation
					sea_,pers_,eke_,time_ = np.array([]),np.array([]),np.array([]),np.array([])
					for ind in sorted(set(tmp_index)):
						indices_of_mon = np.where(tmp_index==ind)[0]
						eke_ = np.append(eke_,tmp_eke[indices_of_mon][0])
						pers_ = np.append(pers_,tmp_pers[indices_of_mon].max())
						sea_ = np.append(sea_,tmp_sea[indices_of_mon][0])
						time_ = np.append(time_,tmp_time[indices_of_mon][np.argmax(tmp_pers[indices_of_mon])])

					# detrend
					slope, intercept, r_value, p_value, std_err = stats.linregress(time_,pers_)
					pers=pers_-(intercept+slope*time_)+np.nanmean(pers_)
					slope, intercept, r_value, p_value, std_err = stats.linregress(time_,eke_)
					eke=eke_-(intercept+slope*time_)+np.nanmean(eke_)

					for season_name,season_id in seasons.items():
						cor_eke_longest['corrcoef'][season_name,y,x],cor_eke_longest['p_value'][season_name,y,x]=stats.pearsonr(pers[sea_==season_id],eke[sea_==season_id])



	da.Dataset(cor_eke).write_nc(working_path+scenario+'/corEKE_'+'_'.join([model,scenario,run])+'_warm.nc')

	da.Dataset(cor_eke_longest).write_nc(working_path+scenario+'/corEKElongest_'+'_'.join([model,scenario,run])+'_warm.nc')
