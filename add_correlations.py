import os,sys,glob,time,collections,signal
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import random as random
import dimarray as da
import subprocess as sub
import scipy.stats as stats

sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
import __settings
model_dict=__settings.model_dict

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
from persistence_functions import *

model=sys.argv[1]
scenario=sys.argv[2]
print model,scenario

in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

try:
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
	working_path='data/'+model+'/'


for run in sorted([path.split('/')[-1].split('_')[-2] for path in glob.glob(working_path+scenario+'/tas*period.nc')]):
	data=da.read_nc(glob.glob(working_path+scenario+'/tas*'+run+'*period.nc')[0])

	cor_eke,cor_spi={},{}
	for stat in ['pearson','pearson_sig','slope','intercept','r_value','p_value','std_err']:
		cor_eke[stat]=da.DimArray(axes=[range(4),[-1,1],data.lat,data.lon],dims=['season','state','lat','lon'])
		cor_spi[stat]=da.DimArray(axes=[range(4),[-1,1],data.lat,data.lon],dims=['season','state','lat','lon'])

	for y in data.lat:
		print(y)
		for x in data.lon:
			period_state=data['period_state'][:,y,x]
			if np.sum(np.abs(period_state))!=0:
				for state in [-1,1]:
					for season in range(4):
						select=(period_state==state) & (data['period_season'][:,y,x]==season)
						tmp_pers=data['period_length'][select,y,x]
						tmp_eke=data['period_eke'][select,y,x]
						tmp_spi=data['period_spi'][select,y,x]
						time=data['period_midpoints'][select,y,x]

						# detrend
						slope, intercept, r_value, p_value, std_err = stats.linregress(time,tmp_pers)
						pers=tmp_pers-(intercept+slope*time)+ptmp_ers.mean()

						slope, intercept, r_value, p_value, std_err = stats.linregress(time,tmp_eke)
						eke=tmp_eke-(intercept+slope*time)+tmp_eke.mean()

						slope, intercept, r_value, p_value, std_err = stats.linregress(time,tmp_spi)
						spi=tmp_spi-(intercept+slope*time)+tmp_spi.mean()

						for toCor,toCor_out in zip([eke,spi],[cor_eke,cor_spi]):
							pearson,pearson_sig=stats.pearsonr(pers,toCor)
							slope,intercept,r_value,p_value,std_err = stats.linregress(toCor,pers)
							for stat_name,stat in zip(['pearson','pearson_sig','slope','intercept','r_value','p_value','std_err'],[pearson,pearson_sig,slope,intercept,r_value,p_value,std_err]):
								toCor_out[stat_name][season,state,y,x]=stat


	ds=da.Dataset(cor_eke)
	ds.write_nc(working_path+scenatio+'/corEKE_'+'_'.join([model,scenario,run])+'.nc')

	ds=da.Dataset(cor_spi)
	ds.write_nc(working_path+scenatio+'/corSPI_'+'_'.join([model,scenario,run])+'.nc')

	asdas
