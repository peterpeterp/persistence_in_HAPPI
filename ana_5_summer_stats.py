import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

model=sys.argv[1]
print model

overwrite=True

working_path='/global/cscratch1/sd/pepflei/'+model+'/'

period_number_limit=70
qu_90=da.read_nc('data/'+model+'_SummaryMeanQu.nc')['SummaryMeanQu'][:,'JJA','warm','qu_90']

for scenario in ['Plus20-Future','Plus15-Future','All-Hist']:
	out_file=working_path+'/'+model+'_'+scenario+'_summerQ90.nc'
	if overwrite and os.path.isfile(out_file):	os.system('rm '+out_file)
	if os.path.isfile(out_file)==False:
		all_files=glob.glob(working_path+scenario+'/*period*')
		runs=[str(ff.split('_')[-2].split('.')[0]) for ff in all_files]

		stat_Xpers_cum_heat=da.DimArray(axes=[np.asarray(runs),np.asarray(range(period_number_limit),np.int32),qu_90.lat,qu_90.lon],dims=['run','ID','lat','lon'])
		stat_Xpers_mean_temp=da.DimArray(axes=[np.asarray(runs),np.asarray(range(period_number_limit),np.int32),qu_90.lat,qu_90.lon],dims=['run','ID','lat','lon'])
		stat_Xpers_hot_shift=da.DimArray(axes=[np.asarray(runs),np.asarray(range(period_number_limit),np.int32),qu_90.lat,qu_90.lon],dims=['run','ID','lat','lon'])
		stat_Xpers_hot_temp=da.DimArray(axes=[np.asarray(runs),np.asarray(range(period_number_limit),np.int32),qu_90.lat,qu_90.lon],dims=['run','ID','lat','lon'])
		stat_TXx_in_Xpers=da.DimArray(axes=[np.asarray(runs),np.arange(0,10,1),qu_90.lat,qu_90.lon],dims=['run','year','lat','lon'])

		for per_file in all_files:
			start_time=time.time()
			run=str(per_file.split('_')[-2].split('.')[0])
			print per_file,run
			nc_in=Dataset(per_file,'r')
			per_len=nc_in.variables['period_length'][:,:,:]
			per_mid=nc_in.variables['period_midpoints'][:,:,:]
			per_mid[np.isnan(per_mid)]=0
			nc_in.close()

			nc_raw=Dataset(per_file.replace('_period',''),'r')

			nc_in=Dataset(per_file.replace('period','summer'),'r')
			hot_shift=nc_in.variables['hottest_day_shift'][:,:,:]
			hot_temp=nc_in.variables['hottest_day_temp'][:,:,:]
			cum_heat=nc_in.variables['cumulated_heat'][:,:,:]
			summer_events=nc_in.variables['period_id'][:,:,:]
			TXx=nc_in.variables['tasX'][:,:,:]
			nc_in.close()

			for x,lon in zip(range(len(qu_90.lon)),qu_90.lon):
				for y,lat in zip(range(len(qu_90.lat)),qu_90.lat):
					if np.sum(summer_events[:,y,x])!=0:
						tmp=summer_events[:,y,x]
						tmp=tmp[0:np.argmax(tmp)+1]
						summer_ids=np.where(per_len[tmp,y,x]>=qu_90[scenario,lat,lon])[0]
						if len(summer_ids)!=0:
							event_ids=tmp[summer_ids]
							if len(summer_ids)<=period_number_limit:
								stat_Xpers_cum_heat[run,0:len(summer_ids)-1,lat,lon]=cum_heat[summer_ids,y,x]
								stat_Xpers_mean_temp[run,0:len(summer_ids)-1,lat,lon]=cum_heat[summer_ids,y,x]/per_len[event_ids,y,x]
								stat_Xpers_hot_shift[run,0:len(summer_ids)-1,lat,lon]=hot_shift[summer_ids,y,x]
								stat_Xpers_hot_temp[run,0:len(summer_ids)-1,lat,lon]=hot_temp[summer_ids,y,x]


								datevar = num2date(per_mid[event_ids,y,x],units = nc_raw.variables['time'].units,calendar = nc_raw.variables['time'].calendar)
								years=np.array([int(str(date).split("-")[0])	for date in datevar[:]])

								for year,i in zip(sorted(set(years)),np.arange(0,10,1)):
									year_ids=np.where(years==year)
									if np.max(hot_temp[summer_ids[year_ids],y,x])==np.max(TXx[summer_ids[year_ids],y,x]):
										stat_TXx_in_Xpers[run,i,lat,lon]=1
									else:
										stat_TXx_in_Xpers[run,i,lat,lon]=0


			print time.time()-start_time
			nc_raw.close()

			ds=da.Dataset({'90X_cum_heat':stat_Xpers_cum_heat,'90X_hot_shift':stat_Xpers_hot_shift,'90X_hot_temp':stat_Xpers_hot_temp,'90X_mean_temp':stat_Xpers_mean_temp,'TXx_in_90Xpers':stat_TXx_in_Xpers})
			ds.write_nc(out_file, mode='w')
			asdas
