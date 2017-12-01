import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

model_dict={'MIROC5':{'grid':'128x256','path':'/global/cscratch1/sd/pepflei/MIROC/MIROC5/'},
			'NorESM1':{'grid':'192x288','path':'/global/cscratch1/sd/pepflei/NCC/NorESM1-HAPPI/'},
			'ECHAM6-3-LR':{'grid':'96x192','path':'/global/cscratch1/sd/pepflei/MPI-M/ECHAM6-3-LR/'},
			'CAM4-2degree':{'grid':'96x144','path':'/global/cscratch1/sd/pepflei/ETH/CAM4-2degree/'},
}

try:
	model=sys.argv[1]
	print model
	working_path=model_dict[model]['path']
	grid=model_dict[model]['grid']
except:
	model='ECHAM6-3-LR'
	working_path='data/tests/'

overwrite=False
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

		for per_file in all_files:
			start_time=time.time()
			run=str(per_file.split('_')[-2].split('.')[0])
			print per_file,run
			nc_in=Dataset(per_file,'r')
			per_len=nc_in.variables['period_length'][:,:,:]
			nc_in.close()

			nc_in=Dataset(per_file.replace('period','summer'),'r')
			hot_shift=nc_in.variables['hottest_day_shift'][:,:,:]
			hot_temp=nc_in.variables['hottest_day_temp'][:,:,:]
			cum_heat=nc_in.variables['cumulated_heat'][:,:,:]
			summer_events=nc_in.variables['period_id'][:,:,:]
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
							else:
								print summer_ids
								print per_len[event_ids,y,x]
								print lon,lat
								print len(summer_ids)
								asdasd
								stat_Xpers_cum_heat[run,:,lat,lon]=cum_heat[summer_ids[0:period_number_limit],y,x]
								stat_Xpers_hot_shift[run,:,lat,lon]=hot_shift[summer_ids[0:period_number_limit],y,x]
								stat_Xpers_hot_temp[run,:,lat,lon]=hot_temp[summer_ids[0:period_number_limit],y,x]

			print time.time()-start_time

		ds=da.Dataset({'90X_cum_heat':stat_Xpers_cum_heat,'90X_hot_shift':stat_Xpers_hot_shift,'90X_hot_temp':stat_Xpers_hot_temp,'90X_mean_temp':stat_Xpers_mean_temp})
		ds.write_nc(out_file, mode='w')
