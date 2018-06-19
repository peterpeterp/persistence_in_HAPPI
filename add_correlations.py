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

try:
	model=sys.argv[1]
	scenario=sys.argv[2]
	print model,scenario
except:
	model='CAM4-2degree'
	scenario='All-Hist'

in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

try:
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
	working_path='data/'+model+'/'


run_list=sorted([path.split('/')[-1].split('_')[-2] for path in glob.glob(working_path+scenario+'/tas*period.nc')])
if run_list==[]:
	run_list=['ens0030']

for run in run_list:
	data=da.read_nc(glob.glob(working_path+scenario+'/tas*'+run+'*period.nc')[0])
	#data=da.read_nc('data/tests/tas_Aday_CAM4-2degree_All-Hist_est1_v1-0_ens0030_period.nc')

	if len(data.keys()):

		cor_eke,cor_spi={},{}
		for stat in ['corrcoef','p_value']:
			cor_eke[stat]=da.DimArray(axes=[range(4),[-1,1],data.lat,data.lon],dims=['season','state','lat','lon'])
			cor_spi[stat]=da.DimArray(axes=[range(4),[-1,1],data.lat,data.lon],dims=['season','state','lat','lon'])


		print('\n'+run+'\n10------50-------100')
		for y,progress in zip(data.lat,np.array([['-']+['']*(len(data.lat)/20+1)]*20).flatten()[0:len(data.lat)]):
			sys.stdout.write(progress); sys.stdout.flush()
			for x in data.lon:
				period_state=data['period_state'][:,y,x]
				if np.sum(np.abs(period_state))!=0:
					for state in [-1,1]:
						state_select=(period_state==state)
						tmp_pers=data['period_length'][state_select,y,x]
						tmp_eke=data['period_eke'][state_select,y,x]
						tmp_spi=data['period_spi'][state_select,y,x]
						time_=data['period_midpoints'][state_select,y,x]

						# detrend
						slope, intercept, r_value, p_value, std_err = stats.linregress(time_,tmp_pers)
						pers=tmp_pers-(intercept+slope*time_)+tmp_pers.mean()

						slope, intercept, r_value, p_value, std_err = stats.linregress(time_,tmp_eke)
						eke=tmp_eke-(intercept+slope*time_)+tmp_eke.mean()

						slope, intercept, r_value, p_value, std_err = stats.linregress(time_,tmp_spi)
						spi=tmp_spi-(intercept+slope*time_)+tmp_spi.mean()

						for season in range(4):
							seas_select=(data['period_season'][state_select,y,x]==season)
							cor_eke['corrcoef'][season,state,y,x],cor_eke['p_value'][season,state,y,x]=stats.pearsonr(pers[seas_select],eke[seas_select])
							cor_spi['corrcoef'][season,state,y,x],cor_spi['p_value'][season,state,y,x]=stats.pearsonr(pers[seas_select],spi[seas_select])



		ds=da.Dataset(cor_eke)
		ds.write_nc(working_path+scenario+'/corEKE_'+'_'.join([model,scenario,run])+'.nc')

		ds=da.Dataset(cor_spi)
		ds.write_nc(working_path+scenario+'/corSPI_'+'_'.join([model,scenario,run])+'.nc')
